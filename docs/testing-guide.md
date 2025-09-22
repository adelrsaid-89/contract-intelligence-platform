# Testing Guide - Contract Intelligence Platform

This comprehensive testing guide covers unit testing, integration testing, API testing, performance testing, and security testing for the Contract Intelligence Platform.

## Testing Strategy Overview

### Test Pyramid Approach

```
                    /\
                   /  \
                  / E2E\    ← End-to-End Tests (Few, Slow, Expensive)
                 /______\
                /        \
               /Integration\  ← Integration Tests (Some, Medium Speed)
              /_____________\
             /               \
            /   Unit Tests    \  ← Unit Tests (Many, Fast, Cheap)
           /_________________\
```

### Testing Levels

1. **Unit Tests**: Test individual components/methods in isolation
2. **Integration Tests**: Test component interactions and data flow
3. **API Tests**: Test REST endpoints with various scenarios
4. **End-to-End Tests**: Test complete user workflows
5. **Performance Tests**: Test system under load
6. **Security Tests**: Test authentication, authorization, and data protection

## 1. Unit Testing

### Backend Unit Tests (.NET 8)

#### Test Framework Setup

```csharp
// Test project dependencies
<PackageReference Include="xUnit" Version="2.4.2" />
<PackageReference Include="xunit.runner.visualstudio" Version="2.4.5" />
<PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
<PackageReference Include="NSubstitute" Version="5.1.0" />
<PackageReference Include="FluentAssertions" Version="6.12.0" />
<PackageReference Include="Microsoft.EntityFrameworkCore.InMemory" Version="8.0.0" />
```

#### Example Unit Tests

```csharp
// Services/ContractServiceTests.cs
public class ContractServiceTests
{
    private readonly IContractRepository _contractRepository;
    private readonly IAiService _aiService;
    private readonly ICurrentUserService _currentUserService;
    private readonly ContractService _contractService;

    public ContractServiceTests()
    {
        _contractRepository = Substitute.For<IContractRepository>();
        _aiService = Substitute.For<IAiService>();
        _currentUserService = Substitute.For<ICurrentUserService>();
        _contractService = new ContractService(_contractRepository, _aiService, _currentUserService);
    }

    [Fact]
    public async Task CreateContractAsync_WithValidData_ShouldCreateContract()
    {
        // Arrange
        var createDto = new CreateContractDto
        {
            ProjectId = 1,
            Title = "Test Contract",
            Value = 1000000m,
            StartDate = DateTime.UtcNow.AddDays(1),
            EndDate = DateTime.UtcNow.AddYears(1)
        };

        var expectedContract = new Contract
        {
            Id = 1,
            ProjectId = createDto.ProjectId,
            Title = createDto.Title,
            Value = createDto.Value
        };

        _contractRepository.CreateAsync(Arg.Any<Contract>())
            .Returns(expectedContract);

        // Act
        var result = await _contractService.CreateContractAsync(createDto);

        // Assert
        result.Should().NotBeNull();
        result.Title.Should().Be(createDto.Title);
        result.Value.Should().Be(createDto.Value);
        await _contractRepository.Received(1).CreateAsync(Arg.Any<Contract>());
    }

    [Fact]
    public async Task ExtractMetadataAsync_WithValidContract_ShouldReturnMetadata()
    {
        // Arrange
        var contractId = 1;
        var contract = new Contract { Id = contractId, Title = "Test Contract" };
        var aiResult = new AiExtractionResult
        {
            Metadata = new List<MetadataField>
            {
                new() { Key = "ProjectName", Value = "Test Project", Confidence = 0.95 }
            }
        };

        _contractRepository.GetByIdAsync(contractId).Returns(contract);
        _aiService.ExtractMetadataAsync(Arg.Any<string>()).Returns(aiResult);

        // Act
        var result = await _contractService.ExtractMetadataAsync(contractId);

        // Assert
        result.Should().NotBeNull();
        result.Metadata.Should().HaveCount(1);
        result.Metadata.First().Key.Should().Be("ProjectName");
        result.Metadata.First().Confidence.Should().Be(0.95);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    [InlineData("   ")]
    public async Task CreateContractAsync_WithInvalidTitle_ShouldThrowValidationException(string invalidTitle)
    {
        // Arrange
        var createDto = new CreateContractDto
        {
            ProjectId = 1,
            Title = invalidTitle,
            Value = 1000000m
        };

        // Act & Assert
        await _contractService.Invoking(x => x.CreateContractAsync(createDto))
            .Should().ThrowAsync<ValidationException>()
            .WithMessage("*Title*required*");
    }
}
```

#### Domain Entity Tests

```csharp
// Entities/AssignmentTests.cs
public class AssignmentTests
{
    [Fact]
    public void Assignment_WhenCreated_ShouldHaveCorrectDefaults()
    {
        // Arrange & Act
        var assignment = new Assignment
        {
            ObligationId = 1,
            AssigneeUserId = 2
        };

        // Assert
        assignment.Status.Should().Be(AssignmentStatus.Open);
        assignment.PercentComplete.Should().Be(0);
        assignment.CreatedAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(1));
    }

    [Theory]
    [InlineData(-1)]
    [InlineData(101)]
    public void UpdateProgress_WithInvalidPercentage_ShouldThrowException(int invalidPercent)
    {
        // Arrange
        var assignment = new Assignment { ObligationId = 1, AssigneeUserId = 2 };

        // Act & Assert
        assignment.Invoking(x => x.UpdateProgress(invalidPercent))
            .Should().Throw<ArgumentOutOfRangeException>();
    }

    [Fact]
    public void UpdateProgress_ToHundredPercent_ShouldSetStatusToDone()
    {
        // Arrange
        var assignment = new Assignment { ObligationId = 1, AssigneeUserId = 2 };

        // Act
        assignment.UpdateProgress(100);

        // Assert
        assignment.PercentComplete.Should().Be(100);
        assignment.Status.Should().Be(AssignmentStatus.Done);
    }
}
```

### Frontend Unit Tests (React/Jest)

#### Test Setup

```json
// package.json
{
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/user-event": "^14.4.3",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0"
  }
}
```

#### Component Tests

```typescript
// __tests__/components/AssignmentCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { AssignmentCard } from '@/components/AssignmentCard';
import { Assignment, AssignmentStatus } from '@/types';

const mockAssignment: Assignment = {
  id: 1,
  obligationDescription: 'Test obligation',
  status: AssignmentStatus.InProgress,
  percentComplete: 50,
  dueDate: new Date('2024-02-15'),
  assigneeName: 'John Doe',
  contractTitle: 'Test Contract'
};

describe('AssignmentCard', () => {
  it('should render assignment details correctly', () => {
    render(<AssignmentCard assignment={mockAssignment} />);

    expect(screen.getByText('Test obligation')).toBeInTheDocument();
    expect(screen.getByText('50%')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByDisplayValue('50')).toBeInTheDocument();
  });

  it('should call onProgressUpdate when progress is changed', async () => {
    const onProgressUpdate = jest.fn();
    render(
      <AssignmentCard
        assignment={mockAssignment}
        onProgressUpdate={onProgressUpdate}
      />
    );

    const progressInput = screen.getByDisplayValue('50');
    fireEvent.change(progressInput, { target: { value: '75' } });
    fireEvent.blur(progressInput);

    expect(onProgressUpdate).toHaveBeenCalledWith(1, 75);
  });

  it('should show overdue warning when assignment is past due', () => {
    const overdueAssignment = {
      ...mockAssignment,
      dueDate: new Date('2024-01-01'),
      status: AssignmentStatus.Overdue
    };

    render(<AssignmentCard assignment={overdueAssignment} />);

    expect(screen.getByText(/overdue/i)).toBeInTheDocument();
    expect(screen.getByTestId('overdue-warning')).toHaveClass('text-red-600');
  });
});
```

#### Service Tests

```typescript
// __tests__/services/api.test.ts
import { ApiService } from '@/services/api';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.get('/api/assignments', (req, res, ctx) => {
    return res(
      ctx.json({
        items: [
          {
            id: 1,
            obligationDescription: 'Test assignment',
            status: 'InProgress',
            percentComplete: 50
          }
        ],
        totalCount: 1
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('ApiService', () => {
  it('should fetch assignments successfully', async () => {
    const result = await ApiService.getAssignments();

    expect(result.items).toHaveLength(1);
    expect(result.items[0].obligationDescription).toBe('Test assignment');
  });

  it('should handle API errors gracefully', async () => {
    server.use(
      rest.get('/api/assignments', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ message: 'Server error' }));
      })
    );

    await expect(ApiService.getAssignments()).rejects.toThrow('Server error');
  });
});
```

### Running Unit Tests

```bash
# Backend tests
cd backend
dotnet test --collect:"XPlat Code Coverage"

# Frontend tests
cd frontend/enova-cip-ui
npm test
npm run test:coverage
```

## 2. Integration Testing

### Backend Integration Tests

#### Database Integration Tests

```csharp
// IntegrationTests/ContractRepositoryTests.cs
public class ContractRepositoryTests : IClassFixture<TestDatabaseFixture>
{
    private readonly TestDatabaseFixture _fixture;
    private readonly ContractRepository _repository;

    public ContractRepositoryTests(TestDatabaseFixture fixture)
    {
        _fixture = fixture;
        _repository = new ContractRepository(_fixture.Context);
    }

    [Fact]
    public async Task CreateAsync_WithValidContract_ShouldPersistToDatabase()
    {
        // Arrange
        var contract = new Contract
        {
            ProjectId = 1,
            Title = "Integration Test Contract",
            Value = 500000m,
            StartDate = DateTime.UtcNow,
            EndDate = DateTime.UtcNow.AddYears(1)
        };

        // Act
        var result = await _repository.CreateAsync(contract);

        // Assert
        result.Id.Should().BeGreaterThan(0);

        var savedContract = await _repository.GetByIdAsync(result.Id);
        savedContract.Should().NotBeNull();
        savedContract.Title.Should().Be("Integration Test Contract");
    }

    [Fact]
    public async Task GetContractsWithObligationsAsync_ShouldIncludeRelatedData()
    {
        // Arrange
        var contract = await _fixture.CreateContractWithObligations();

        // Act
        var result = await _repository.GetContractsWithObligationsAsync(contract.ProjectId);

        // Assert
        result.Should().NotBeEmpty();
        result.First().Obligations.Should().NotBeEmpty();
        result.First().MetadataFields.Should().NotBeEmpty();
    }
}

// TestDatabaseFixture.cs
public class TestDatabaseFixture : IDisposable
{
    public CipDbContext Context { get; private set; }

    public TestDatabaseFixture()
    {
        var options = new DbContextOptionsBuilder<CipDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;

        Context = new CipDbContext(options);
        SeedTestData();
    }

    private void SeedTestData()
    {
        // Add test users, projects, etc.
        var testUser = new User
        {
            Name = "Test User",
            Email = "test@example.com",
            Role = UserRole.Admin,
            PasswordHash = "hashed-password"
        };

        Context.Users.Add(testUser);
        Context.SaveChanges();
    }

    public void Dispose() => Context.Dispose();
}
```

#### API Controller Integration Tests

```csharp
// IntegrationTests/ContractsControllerTests.cs
public class ContractsControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;

    public ContractsControllerTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task GetContracts_WithValidAuth_ShouldReturnContracts()
    {
        // Arrange
        var token = await GetAuthTokenAsync("admin@example.com", "Admin123!");
        _client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", token);

        // Act
        var response = await _client.GetAsync("/api/contracts");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var content = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<PagedResult<ContractDto>>(content);

        result.Should().NotBeNull();
        result.Items.Should().NotBeEmpty();
    }

    [Fact]
    public async Task CreateContract_WithValidData_ShouldCreateAndReturnContract()
    {
        // Arrange
        var token = await GetAuthTokenAsync("admin@example.com", "Admin123!");
        _client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", token);

        var createDto = new CreateContractDto
        {
            ProjectId = 1,
            Title = "API Test Contract",
            Value = 750000m,
            StartDate = DateTime.UtcNow.AddDays(1),
            EndDate = DateTime.UtcNow.AddYears(1)
        };

        var json = JsonSerializer.Serialize(createDto);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        // Act
        var response = await _client.PostAsync("/api/contracts", content);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);

        var responseContent = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<ContractDto>(responseContent);

        result.Should().NotBeNull();
        result.Title.Should().Be("API Test Contract");
    }

    private async Task<string> GetAuthTokenAsync(string email, string password)
    {
        var loginDto = new LoginDto { Email = email, Password = password };
        var json = JsonSerializer.Serialize(loginDto);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _client.PostAsync("/api/auth/login", content);
        var responseContent = await response.Content.ReadAsStringAsync();
        var authResult = JsonSerializer.Deserialize<AuthResult>(responseContent);

        return authResult.AccessToken;
    }
}
```

## 3. API Testing with Postman

### Postman Collection Structure

```json
{
  "info": {
    "name": "Contract Intelligence Platform API",
    "description": "Complete API test suite for CIP"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:5000/api"
    },
    {
      "key": "authToken",
      "value": ""
    }
  ],
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Login Admin",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"admin@example.com\",\n  \"password\": \"Admin123!\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/auth/login",
              "host": ["{{baseUrl}}"],
              "path": ["auth", "login"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Login successful\", function () {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test(\"Token received\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.accessToken).to.exist;",
                  "    pm.collectionVariables.set(\"authToken\", jsonData.accessToken);",
                  "});"
                ]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Automated API Tests

```javascript
// Postman test scripts
pm.test("Response time is less than 200ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(200);
});

pm.test("Content-Type is present", function () {
    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
});

pm.test("Contract creation returns valid ID", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.id).to.be.a('number');
    pm.expect(jsonData.id).to.be.greaterThan(0);
    pm.collectionVariables.set("contractId", jsonData.id);
});

pm.test("RBAC enforcement", function () {
    // Test that manager can only see assigned projects
    var jsonData = pm.response.json();
    var projectIds = jsonData.items.map(item => item.projectId);
    var allowedProjects = pm.collectionVariables.get("managerProjects").split(",");

    projectIds.forEach(projectId => {
        pm.expect(allowedProjects).to.include(projectId.toString());
    });
});
```

### Newman CLI Testing

```bash
# Install Newman
npm install -g newman

# Run collection
newman run CIP-API-Tests.postman_collection.json \
  --environment CIP-Local.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export results.json

# Run with data file
newman run CIP-API-Tests.postman_collection.json \
  --data test-data.csv \
  --iteration-count 10
```

## 4. End-to-End Testing

### Playwright E2E Tests

#### Setup

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    }
  ]
});
```

#### E2E Test Examples

```typescript
// e2e/manager-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Manager Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as manager
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'sarah.johnson@example.com');
    await page.fill('[data-testid="password"]', 'Manager123!');
    await page.click('[data-testid="login-button"]');

    // Wait for dashboard to load
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
  });

  test('should review AI extraction results', async ({ page }) => {
    // Navigate to contracts
    await page.click('[data-testid="nav-contracts"]');

    // Select a contract
    await page.click('[data-testid="contract-1"]');

    // Start AI extraction
    await page.click('[data-testid="extract-metadata-button"]');

    // Wait for extraction to complete
    await expect(page.locator('[data-testid="extraction-results"]')).toBeVisible();

    // Verify extracted fields
    await expect(page.locator('[data-testid="field-ProjectName"]')).toContainText('Transportation Hub');
    await expect(page.locator('[data-testid="field-ContractValue"]')).toContainText('45,750,000');

    // Correct a field
    await page.click('[data-testid="edit-field-ProjectName"]');
    await page.fill('[data-testid="field-value-input"]', 'Regional Transportation Hub Development');
    await page.click('[data-testid="save-field-button"]');

    // Verify correction is saved
    await expect(page.locator('[data-testid="field-ProjectName"]')).toContainText('Regional Transportation Hub Development');
    await expect(page.locator('[data-testid="confidence-score"]')).toContainText('100%');
  });

  test('should create and assign obligations', async ({ page }) => {
    // Navigate to obligations
    await page.goto('/contracts/1/obligations');

    // Extract obligations
    await page.click('[data-testid="extract-obligations-button"]');
    await expect(page.locator('[data-testid="obligations-list"]')).toBeVisible();

    // Select obligations to assign
    await page.check('[data-testid="obligation-1-checkbox"]');
    await page.check('[data-testid="obligation-2-checkbox"]');

    // Create assignment
    await page.click('[data-testid="assign-obligations-button"]');
    await page.selectOption('[data-testid="assignee-select"]', '4'); // Ahmed's user ID
    await page.fill('[data-testid="due-date-input"]', '2024-02-15');
    await page.click('[data-testid="create-assignment-button"]');

    // Verify assignment creation
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Assignments created successfully');

    // Verify assignment appears in dashboard
    await page.goto('/assignments');
    await expect(page.locator('[data-testid="assignment-1"]')).toBeVisible();
  });
});
```

#### Cross-Role E2E Tests

```typescript
// e2e/cross-role-workflow.spec.ts
test('complete assignment workflow across roles', async ({ browser }) => {
  // Create contexts for different users
  const managerContext = await browser.newContext();
  const subcontractorContext = await browser.newContext();

  const managerPage = await managerContext.newPage();
  const subcontractorPage = await subcontractorContext.newPage();

  // Manager creates assignment
  await managerPage.goto('/login');
  await managerPage.fill('[data-testid="email"]', 'sarah.johnson@example.com');
  await managerPage.fill('[data-testid="password"]', 'Manager123!');
  await managerPage.click('[data-testid="login-button"]');

  // ... create assignment steps ...

  // Subcontractor receives and works on assignment
  await subcontractorPage.goto('/login');
  await subcontractorPage.fill('[data-testid="email"]', 'ahmed.rashid@example.com');
  await subcontractorPage.fill('[data-testid="password"]', 'User123!');
  await subcontractorPage.click('[data-testid="login-button"]');

  // Check assignment appears in subcontractor dashboard
  await expect(subcontractorPage.locator('[data-testid="assignment-1"]')).toBeVisible();

  // Update progress
  await subcontractorPage.click('[data-testid="assignment-1"]');
  await subcontractorPage.fill('[data-testid="progress-input"]', '75');
  await subcontractorPage.selectOption('[data-testid="status-select"]', 'InProgress');
  await subcontractorPage.click('[data-testid="update-progress-button"]');

  // Upload evidence
  await subcontractorPage.setInputFiles('[data-testid="evidence-upload"]', 'test-files/sample-report.pdf');
  await subcontractorPage.fill('[data-testid="evidence-description"]', 'Progress report with photos');
  await subcontractorPage.click('[data-testid="upload-evidence-button"]');

  // Verify manager sees updates
  await managerPage.goto('/assignments');
  await expect(managerPage.locator('[data-testid="assignment-1-progress"]')).toContainText('75%');
  await expect(managerPage.locator('[data-testid="assignment-1-evidence"]')).toContainText('1 file');
});
```

## 5. Performance Testing

### Load Testing with k6

```javascript
// performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up
    { duration: '5m', target: 50 }, // Stay at 50 users
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.02'],   // Error rate under 2%
  },
};

const BASE_URL = 'http://localhost:5000/api';

// Login and get token
function authenticate() {
  const loginResponse = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    email: 'admin@example.com',
    password: 'Admin123!'
  }), {
    headers: { 'Content-Type': 'application/json' }
  });

  check(loginResponse, {
    'login successful': (r) => r.status === 200,
    'token received': (r) => JSON.parse(r.body).accessToken !== undefined,
  });

  return JSON.parse(loginResponse.body).accessToken;
}

export default function () {
  const token = authenticate();
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  // Test various endpoints
  const endpoints = [
    '/projects',
    '/contracts',
    '/assignments',
    '/dashboard/overview'
  ];

  endpoints.forEach(endpoint => {
    const response = http.get(`${BASE_URL}${endpoint}`, { headers });

    check(response, {
      [`${endpoint} status is 200`]: (r) => r.status === 200,
      [`${endpoint} response time < 500ms`]: (r) => r.timings.duration < 500,
    });
  });

  sleep(1);
}
```

### Database Performance Tests

```sql
-- performance/database-benchmarks.sql

-- Test query performance with large datasets
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

-- Test 1: Contract search with filters
SELECT c.Id, c.Title, c.Value, p.Name as ProjectName
FROM Contracts c
INNER JOIN Projects p ON c.ProjectId = p.Id
WHERE c.Status = 1 -- Active
  AND c.Value > 1000000
  AND c.StartDate >= DATEADD(year, -1, GETDATE())
ORDER BY c.Value DESC;

-- Test 2: Assignment aggregation
SELECT
    u.Name,
    COUNT(a.Id) as TotalAssignments,
    AVG(CAST(a.PercentComplete AS FLOAT)) as AvgProgress,
    COUNT(CASE WHEN a.Status = 3 THEN 1 END) as OverdueCount
FROM Users u
LEFT JOIN Assignments a ON u.Id = a.AssigneeUserId
GROUP BY u.Id, u.Name
ORDER BY OverdueCount DESC;

-- Test 3: Complex obligation search
SELECT
    o.Id,
    o.Description,
    c.Title as ContractTitle,
    p.Name as ProjectName,
    COUNT(a.Id) as AssignmentCount,
    SUM(CASE WHEN a.Status = 2 THEN 1 ELSE 0 END) as CompletedCount
FROM Obligations o
INNER JOIN Contracts c ON o.ContractId = c.Id
INNER JOIN Projects p ON c.ProjectId = p.Id
LEFT JOIN Assignments a ON o.Id = a.ObligationId
WHERE o.DueDate BETWEEN GETDATE() AND DATEADD(month, 1, GETDATE())
GROUP BY o.Id, o.Description, c.Title, p.Name
ORDER BY o.DueDate;

SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
```

## 6. Security Testing

### Authentication and Authorization Tests

```csharp
// SecurityTests/AuthenticationTests.cs
public class AuthenticationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public AuthenticationTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task AccessProtectedEndpoint_WithoutToken_ShouldReturn401()
    {
        // Act
        var response = await _client.GetAsync("/api/contracts");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task AccessProtectedEndpoint_WithInvalidToken_ShouldReturn401()
    {
        // Arrange
        _client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", "invalid-token");

        // Act
        var response = await _client.GetAsync("/api/contracts");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task AccessAdminEndpoint_AsManager_ShouldReturn403()
    {
        // Arrange
        var managerToken = await GetTokenForRole(UserRole.Manager);
        _client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", managerToken);

        // Act
        var response = await _client.PostAsync("/api/users",
            new StringContent("{}", Encoding.UTF8, "application/json"));

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }

    [Theory]
    [InlineData("'; DROP TABLE Users; --")]
    [InlineData("<script>alert('xss')</script>")]
    [InlineData("../../../etc/passwd")]
    public async Task CreateContract_WithMaliciousInput_ShouldBeSanitized(string maliciousInput)
    {
        // Arrange
        var token = await GetTokenForRole(UserRole.Admin);
        _client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", token);

        var createDto = new
        {
            ProjectId = 1,
            Title = maliciousInput,
            Value = 1000000
        };

        // Act
        var response = await _client.PostAsync("/api/contracts",
            new StringContent(JsonSerializer.Serialize(createDto),
                Encoding.UTF8, "application/json"));

        // Assert
        if (response.IsSuccessStatusCode)
        {
            var content = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<ContractDto>(content);
            result.Title.Should().NotContain("<script>");
            result.Title.Should().NotContain("DROP TABLE");
            result.Title.Should().NotContain("../");
        }
    }
}
```

### Penetration Testing Checklist

```bash
# OWASP ZAP Security Scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:3000

# SQL Injection Tests
sqlmap -u "http://localhost:5000/api/contracts?search=test" \
  --cookie="Authorization=Bearer <token>" \
  --risk=3 --level=5

# XSS Testing
python3 xsser.py --url "http://localhost:3000/contracts" \
  --cookie="authToken=<token>"

# CSRF Testing
csrf-poc --url http://localhost:3000 \
  --method POST \
  --data '{"title":"test"}'
```

## 7. Test Data Management

### Test Database Setup

```csharp
// TestHelpers/DatabaseTestFixture.cs
public class DatabaseTestFixture : IDisposable
{
    public CipDbContext Context { get; private set; }
    private readonly string _connectionString;

    public DatabaseTestFixture()
    {
        _connectionString = $"Server=(localdb)\\mssqllocaldb;Database=CipTestDb_{Guid.NewGuid()};Trusted_Connection=true;";

        var options = new DbContextOptionsBuilder<CipDbContext>()
            .UseSqlServer(_connectionString)
            .Options;

        Context = new CipDbContext(options);
        Context.Database.EnsureCreated();
        SeedTestData();
    }

    private void SeedTestData()
    {
        // Create test users
        var admin = new User
        {
            Name = "Test Admin",
            Email = "testadmin@example.com",
            Role = UserRole.Admin,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("TestPassword123!")
        };

        var manager = new User
        {
            Name = "Test Manager",
            Email = "testmanager@example.com",
            Role = UserRole.Manager,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("TestPassword123!")
        };

        Context.Users.AddRange(admin, manager);

        // Create test project
        var project = new Project
        {
            Name = "Test Project",
            ClientName = "Test Client",
            Country = "Test Country",
            Status = ProjectStatus.Active
        };

        Context.Projects.Add(project);
        Context.SaveChanges();

        // Grant manager access to project
        var permission = new UserProjectPermission
        {
            UserId = manager.Id,
            ProjectId = project.Id,
            AccessLevel = AccessLevel.Manager
        };

        Context.UserProjectPermissions.Add(permission);
        Context.SaveChanges();
    }

    public void Dispose()
    {
        Context.Database.EnsureDeleted();
        Context.Dispose();
    }
}
```

### Test Data Builders

```csharp
// TestHelpers/Builders/ContractBuilder.cs
public class ContractBuilder
{
    private Contract _contract;

    public ContractBuilder()
    {
        _contract = new Contract
        {
            Title = "Test Contract",
            ProjectId = 1,
            Value = 1000000,
            StartDate = DateTime.UtcNow,
            EndDate = DateTime.UtcNow.AddYears(1),
            Status = ContractStatus.Active
        };
    }

    public ContractBuilder WithTitle(string title)
    {
        _contract.Title = title;
        return this;
    }

    public ContractBuilder WithValue(decimal value)
    {
        _contract.Value = value;
        return this;
    }

    public ContractBuilder WithProject(int projectId)
    {
        _contract.ProjectId = projectId;
        return this;
    }

    public ContractBuilder WithObligations(int count)
    {
        _contract.Obligations = Enumerable.Range(1, count)
            .Select(i => new Obligation
            {
                Description = $"Test Obligation {i}",
                Frequency = "Monthly",
                DueDate = DateTime.UtcNow.AddDays(30 * i),
                PenaltyText = $"${i * 1000} penalty",
                Source = DataSource.AI,
                Confidence = 0.9
            })
            .ToList();

        return this;
    }

    public Contract Build() => _contract;
}

// Usage in tests
var contract = new ContractBuilder()
    .WithTitle("Test Infrastructure Contract")
    .WithValue(5000000)
    .WithObligations(5)
    .Build();
```

## 8. CI/CD Pipeline Testing

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    services:
      sqlserver:
        image: mcr.microsoft.com/mssql/server:2019-latest
        env:
          SA_PASSWORD: TestPassword123!
          ACCEPT_EULA: Y
        ports:
          - 1433:1433

    steps:
    - uses: actions/checkout@v3

    - name: Setup .NET
      uses: actions/setup-dotnet@v3
      with:
        dotnet-version: 8.0.x

    - name: Restore dependencies
      run: dotnet restore ./backend

    - name: Build
      run: dotnet build ./backend --no-restore

    - name: Run unit tests
      run: dotnet test ./backend --no-build --verbosity normal --collect:"XPlat Code Coverage"

    - name: Generate coverage report
      run: |
        dotnet tool install -g dotnet-reportgenerator-globaltool
        reportgenerator -reports:"backend/**/coverage.cobertura.xml" -targetdir:"coverage" -reporttypes:"Html;Cobertura"

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: 18

    - name: Install dependencies
      run: npm ci
      working-directory: ./frontend/enova-cip-ui

    - name: Run tests
      run: npm test -- --coverage --watchAll=false
      working-directory: ./frontend/enova-cip-ui

    - name: Run build
      run: npm run build
      working-directory: ./frontend/enova-cip-ui

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: 18

    - name: Install dependencies
      run: npm ci

    - name: Install Playwright
      run: npx playwright install --with-deps

    - name: Start services
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 30

    - name: Run E2E tests
      run: npx playwright test

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: playwright-report
        path: playwright-report/
```

## 9. Test Reporting and Metrics

### Coverage Requirements

- **Unit Tests**: Minimum 80% code coverage
- **Integration Tests**: All critical user paths covered
- **API Tests**: All endpoints tested with auth scenarios
- **E2E Tests**: Complete user workflows for each role

### Test Metrics Dashboard

```json
{
  "testSummary": {
    "totalTests": 450,
    "passed": 445,
    "failed": 3,
    "skipped": 2,
    "coverage": {
      "lines": 87.3,
      "branches": 82.1,
      "functions": 91.2,
      "statements": 86.8
    }
  },
  "performance": {
    "averageResponseTime": "145ms",
    "p95ResponseTime": "380ms",
    "errorRate": "0.8%"
  },
  "security": {
    "vulnerabilities": 0,
    "authTestsPassed": 100,
    "xssTestsPassed": 95,
    "sqlInjectionTestsPassed": 100
  }
}
```

This comprehensive testing guide ensures the Contract Intelligence Platform maintains high quality, security, and performance standards across all components and user workflows.