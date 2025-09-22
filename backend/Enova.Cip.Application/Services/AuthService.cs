using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using AutoMapper;
using BCrypt.Net;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Domain.Interfaces;

namespace Enova.Cip.Application.Services;

public class AuthService : IAuthService
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly IMapper _mapper;
    private readonly IConfiguration _configuration;
    private readonly ILogger<AuthService> _logger;
    private readonly Dictionary<string, string> _refreshTokens = new();

    public AuthService(IUnitOfWork unitOfWork, IMapper mapper, IConfiguration configuration, ILogger<AuthService> logger)
    {
        _unitOfWork = unitOfWork;
        _mapper = mapper;
        _configuration = configuration;
        _logger = logger;
    }

    public async Task<AuthResponseDto> LoginAsync(LoginDto loginDto, CancellationToken cancellationToken = default)
    {
        var user = await _unitOfWork.Users.FindFirstAsync(u => u.Email == loginDto.Email && u.IsActive, cancellationToken);

        if (user == null || !BCrypt.Net.BCrypt.Verify(loginDto.Password, user.PasswordHash))
        {
            throw new UnauthorizedAccessException("Invalid email or password");
        }

        var token = GenerateJwtToken(user);
        var refreshToken = GenerateRefreshToken();
        var expiresAt = DateTime.UtcNow.AddMinutes(GetJwtExpiryMinutes());

        _refreshTokens[refreshToken] = user.Id.ToString();

        var userDto = _mapper.Map<UserDto>(user);

        return new AuthResponseDto
        {
            Token = token,
            RefreshToken = refreshToken,
            User = userDto,
            ExpiresAt = expiresAt
        };
    }

    public async Task<AuthResponseDto> RefreshTokenAsync(string refreshToken, CancellationToken cancellationToken = default)
    {
        if (!_refreshTokens.TryGetValue(refreshToken, out var userIdStr) || !int.TryParse(userIdStr, out var userId))
        {
            throw new UnauthorizedAccessException("Invalid refresh token");
        }

        var user = await _unitOfWork.Users.GetByIdAsync(userId, cancellationToken);
        if (user == null || !user.IsActive)
        {
            _refreshTokens.Remove(refreshToken);
            throw new UnauthorizedAccessException("User not found or inactive");
        }

        var token = GenerateJwtToken(user);
        var newRefreshToken = GenerateRefreshToken();
        var expiresAt = DateTime.UtcNow.AddMinutes(GetJwtExpiryMinutes());

        _refreshTokens.Remove(refreshToken);
        _refreshTokens[newRefreshToken] = user.Id.ToString();

        var userDto = _mapper.Map<UserDto>(user);

        return new AuthResponseDto
        {
            Token = token,
            RefreshToken = newRefreshToken,
            User = userDto,
            ExpiresAt = expiresAt
        };
    }

    public async Task<UserDto> GetCurrentUserAsync(int userId, CancellationToken cancellationToken = default)
    {
        var user = await _unitOfWork.Users.GetByIdAsync(userId, cancellationToken);
        if (user == null)
        {
            throw new UnauthorizedAccessException("User not found");
        }

        return _mapper.Map<UserDto>(user);
    }

    public Task<bool> ValidateTokenAsync(string token, CancellationToken cancellationToken = default)
    {
        try
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.ASCII.GetBytes(GetJwtSecret());

            tokenHandler.ValidateToken(token, new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ValidateIssuer = false,
                ValidateAudience = false,
                ClockSkew = TimeSpan.Zero
            }, out SecurityToken validatedToken);

            return Task.FromResult(true);
        }
        catch
        {
            return Task.FromResult(false);
        }
    }

    public Task LogoutAsync(string refreshToken, CancellationToken cancellationToken = default)
    {
        _refreshTokens.Remove(refreshToken);
        return Task.CompletedTask;
    }

    private string GenerateJwtToken(Domain.Entities.User user)
    {
        var tokenHandler = new JwtSecurityTokenHandler();
        var key = Encoding.ASCII.GetBytes(GetJwtSecret());

        var tokenDescriptor = new SecurityTokenDescriptor
        {
            Subject = new ClaimsIdentity(new[]
            {
                new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
                new Claim(ClaimTypes.Email, user.Email),
                new Claim(ClaimTypes.Name, user.Name),
                new Claim(ClaimTypes.Role, user.Role.ToString())
            }),
            Expires = DateTime.UtcNow.AddMinutes(GetJwtExpiryMinutes()),
            SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
        };

        var token = tokenHandler.CreateToken(tokenDescriptor);
        return tokenHandler.WriteToken(token);
    }

    private string GenerateRefreshToken()
    {
        return Guid.NewGuid().ToString();
    }

    private string GetJwtSecret()
    {
        return _configuration["Jwt:Secret"] ?? throw new InvalidOperationException("JWT Secret not configured");
    }

    private int GetJwtExpiryMinutes()
    {
        return int.Parse(_configuration["Jwt:ExpiryMinutes"] ?? "60");
    }
}