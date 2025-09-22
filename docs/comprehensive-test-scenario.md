# Comprehensive Test Scenario - Contract Intelligence Platform

## Test Overview
This document defines comprehensive test scenarios based on the Enova Contract Intelligence Platform use case. It covers all 15 phases of the workflow and validates all acceptance criteria.

## Test Environment Setup
- **System**: Full Docker Compose deployment with SEED_MODE=example
- **Test Data**: Dynamic projects, users, contracts (no hardcoded values)
- **AI Providers**: Both local and cloud providers (if configured)
- **Browser**: Chrome/Firefox for frontend testing
- **API Testing**: Postman/curl for backend validation

## Test Scenarios

### 1. RBAC and Security Validation

#### Test 1.1: Authentication and Role-Based Access
**Objective**: Verify JWT authentication and role-based navigation

**Steps**:
1. Access frontend without authentication → Should redirect to login
2. Login with Admin credentials → Should show admin sidebar
3. Login with Manager credentials → Should show manager sidebar
4. Login with Subcontractor credentials → Should show limited sidebar
5. Verify JWT token refresh functionality
6. Test session timeout and logout

**Expected Results**:
- ✅ Proper redirects and access control
- ✅ Role-specific UI components
- ✅ Secure token handling

#### Test 1.2: Project-Level Permissions (UserProjectPermissions)
**Objective**: Verify managers only see assigned projects

**Steps**:
1. Login as Manager 1 → Should only see assigned projects
2. Try to access other project via API → Should get 403 Forbidden
3. Admin assigns new project → Manager should see it immediately
4. Admin revokes access → Manager should lose access

**Expected Results**:
- ✅ No cross-project data leaks
- ✅ Dynamic permission updates
- ✅ API-level enforcement

### 2. Admin Workflow Tests

#### Test 2.1: Project and User Management
**Objective**: Validate dynamic project creation and user management

**Steps**:
1. Create new project "Metro Expansion Project"
2. Create new manager user "alex.metro@example.com"
3. Grant manager Owner access to Metro project
4. Create new subcontractor "metro.sub@example.com"
5. Verify all users appear in system with correct roles

**Expected Results**:
- ✅ Projects created without code changes
- ✅ Users assigned to projects dynamically
- ✅ No hardcoded assumptions

#### Test 2.2: Global Dashboard and KPIs
**Objective**: Verify admin sees global metrics

**Steps**:
1. Check global compliance percentage
2. Verify overdue obligations count
3. Check penalty risk totals
4. View project overview grid
5. Validate CAFM placeholders present

**Expected Results**:
- ✅ Accurate global metrics
- ✅ Real-time data updates
- ✅ Cross-project visibility

### 3. Manager Workflow Tests

#### Test 3.1: Contract Upload and Repository Management
**Objective**: Test contract upload and folder organization

**Steps**:
1. Login as Manager
2. Navigate to assigned project
3. Upload contract PDF to "Contract/" folder
4. Upload amendments to "AMCs/" folder
5. Verify file versioning works
6. Check audit logs for upload events

**Expected Results**:
- ✅ Proper folder organization
- ✅ Version control tracking
- ✅ Audit trail creation

#### Test 3.2: AI Metadata Extraction and Review
**Objective**: Test AI extraction and human correction workflow

**Steps**:
1. Upload sample contract PDF
2. Trigger metadata extraction
3. Review AI results with confidence scores
4. Correct 2-3 fields with manual input
5. Save corrected metadata
6. Verify both AI and human versions stored

**Expected Results**:
- ✅ AI extraction returns structured data
- ✅ Confidence scores displayed
- ✅ Human corrections tracked
- ✅ Provenance maintained

#### Test 3.3: Obligation Extraction and Management
**Objective**: Test obligation extraction and assignment workflow

**Steps**:
1. Extract obligations from uploaded contract
2. Review AI-extracted obligations (>6 expected)
3. Edit/correct obligation descriptions
4. Verify frequency detection (daily, monthly, etc.)
5. Check penalty clause extraction
6. Save corrected obligations

**Expected Results**:
- ✅ >80% obligation coverage achieved
- ✅ Accurate frequency detection
- ✅ Penalty texts extracted
- ✅ Human corrections saved

#### Test 3.4: Assignment Creation
**Objective**: Test obligation assignment to users

**Steps**:
1. Select 3 obligations for assignment
2. Assign 1 to internal team member
3. Assign 2 to subcontractor
4. Set due dates and priority levels
5. Verify assignment notifications sent
6. Check dashboard updates reflect assignments

**Expected Results**:
- ✅ Immediate notification emails
- ✅ Assignment status tracking
- ✅ Dashboard updates real-time

### 4. Subcontractor Workflow Tests

#### Test 4.1: Task Visibility and Access Control
**Objective**: Verify subcontractors only see assigned tasks

**Steps**:
1. Login as subcontractor
2. Check visible obligations (should only be assigned ones)
3. Try to access other projects via API → Should fail
4. Verify task details accessible
5. Check due dates and penalty information visible

**Expected Results**:
- ✅ Only assigned tasks visible
- ✅ No access to other data
- ✅ Complete task information shown

#### Test 4.2: Kanban Board and Progress Tracking
**Objective**: Test task management interface

**Steps**:
1. View tasks in Kanban layout (To-Do, In-Progress, Done)
2. Drag task from To-Do → In-Progress
3. Update progress percentage to 25%
4. Drag task to Done at 100%
5. Verify status changes reflected in backend
6. Check manager receives progress notifications

**Expected Results**:
- ✅ Smooth drag-drop functionality
- ✅ Progress tracking works
- ✅ Manager notifications sent
- ✅ Real-time updates

#### Test 4.3: Evidence Upload and Validation
**Objective**: Test evidence submission workflow

**Steps**:
1. Select in-progress task
2. Upload evidence file (invoice PDF)
3. Add description note
4. Submit for manager review
5. Mark task as complete
6. Verify manager gets validation request

**Expected Results**:
- ✅ File upload successful
- ✅ Metadata captured correctly
- ✅ Manager notification sent
- ✅ Task status updated

### 5. AI Features Testing

#### Test 5.1: OCR Capabilities
**Objective**: Test document text extraction

**Steps**:
1. Upload scanned PDF contract
2. Test local OCR (Tesseract)
3. If configured, test Azure Document Intelligence
4. Verify text extraction quality
5. Check layout preservation
6. Test batch processing

**Expected Results**:
- ✅ Readable text extracted
- ✅ Layout information preserved
- ✅ Provider switching works
- ✅ Batch processing functional

#### Test 5.2: Natural Language Q&A System
**Objective**: Test structured data querying

**Steps**:
1. Ask: "Obligations due this month for Metro Expansion?"
2. Ask: "What are the SLAs for cleaning in Shopping Center project?"
3. Ask: "Show common obligations between both projects"
4. Ask: "List overdue obligations for subcontractors"
5. Apply filters (project, contractor, status)
6. Verify deep links to source data work

**Expected Results**:
- ✅ Accurate answers from structured data
- ✅ Filter functionality works
- ✅ Deep links navigate correctly
- ✅ Performance acceptable (<5 seconds)

### 6. Notification and Reminder System

#### Test 6.1: T-14 Day Reminder Logic
**Objective**: Test automated reminder system

**Steps**:
1. Create obligation due in 15 days
2. Wait for system to send T-14 reminder (or simulate)
3. Verify daily reminders continue until completion
4. Test reminder stops when task completed
5. Check overdue notifications trigger
6. Verify manager penalty risk alerts

**Expected Results**:
- ✅ T-14 day reminders start correctly
- ✅ Daily frequency maintained
- ✅ Reminders stop on completion
- ✅ Overdue alerts generated
- ✅ Penalty risk calculated

#### Test 6.2: Email Notification System
**Objective**: Verify email delivery (via MailHog)

**Steps**:
1. Check MailHog interface (localhost:8025)
2. Trigger assignment notification
3. Verify email content and formatting
4. Test reminder email templates
5. Check overdue alert emails
6. Validate email addresses and routing

**Expected Results**:
- ✅ Emails appear in MailHog
- ✅ Professional formatting
- ✅ Correct recipient targeting
- ✅ Template rendering works

### 7. Dashboard and KPI Validation

#### Test 7.1: Manager Dashboard Metrics
**Objective**: Verify project-specific KPIs

**Steps**:
1. Check project completion percentages
2. Verify subcontractor performance metrics
3. Review upcoming obligations calendar
4. Check penalty risk indicators
5. Validate data filtering by project
6. Test drill-down navigation

**Expected Results**:
- ✅ Accurate project metrics
- ✅ Real-time data updates
- ✅ Proper data isolation
- ✅ Navigation links work

#### Test 7.2: Subcontractor Dashboard
**Objective**: Verify personal productivity view

**Steps**:
1. Check personal task completion rates
2. Review upcoming deadlines
3. Verify evidence upload history
4. Check progress tracking charts
5. Test task quick actions
6. Validate notification center

**Expected Results**:
- ✅ Personal metrics accurate
- ✅ Deadline visibility clear
- ✅ Upload history complete
- ✅ Quick actions functional

### 8. Search and Data Management

#### Test 8.1: Elasticsearch Integration
**Objective**: Test search functionality

**Steps**:
1. Search for contracts by client name
2. Filter by date ranges
3. Search obligations by description keywords
4. Test faceted search with multiple filters
5. Verify search result relevance
6. Check search performance

**Expected Results**:
- ✅ Fast search responses (<2 seconds)
- ✅ Relevant results returned
- ✅ Filters work correctly
- ✅ Elasticsearch sync operational

#### Test 8.2: File Storage and Versioning
**Objective**: Test MinIO integration and versioning

**Steps**:
1. Upload multiple versions of same contract
2. Check version history preservation
3. Test file download URLs
4. Verify MinIO bucket organization
5. Test large file uploads (>10MB)
6. Check storage quotas and limits

**Expected Results**:
- ✅ All versions stored
- ✅ Download links work
- ✅ Proper bucket structure
- ✅ Large file handling
- ✅ Storage limits enforced

### 9. System Performance and Reliability

#### Test 9.1: Load Testing
**Objective**: Test system under load

**Steps**:
1. Simulate 10 concurrent users uploading files
2. Test 50 simultaneous searches
3. Generate 100 notification emails
4. Process multiple AI extractions in parallel
5. Monitor resource usage
6. Check response times under load

**Expected Results**:
- ✅ System remains responsive
- ✅ No timeouts or errors
- ✅ Reasonable resource usage
- ✅ Graceful degradation

#### Test 9.2: Error Handling and Recovery
**Objective**: Test system resilience

**Steps**:
1. Simulate database connection loss
2. Test MinIO service interruption
3. Cause Elasticsearch downtime
4. Test AI service failures
5. Verify graceful error messages
6. Check system recovery after restart

**Expected Results**:
- ✅ Graceful error handling
- ✅ User-friendly error messages
- ✅ Service recovery works
- ✅ No data corruption

### 10. Acceptance Criteria Validation

#### Test 10.1: Dynamic System Requirements
**Objective**: Verify no hardcoded values

**Steps**:
1. Create project with Arabic name "مشروع المطار الجديد"
2. Create user with different email domain
3. Change project names via UI
4. Verify all lists/dashboards update
5. Test with SEED_MODE=none (empty system)
6. Confirm system works without sample data

**Expected Results**:
- ✅ Arabic names supported
- ✅ Any email domain works
- ✅ Dynamic updates everywhere
- ✅ Empty system functional

#### Test 10.2: AI Accuracy Targets
**Objective**: Verify AI extraction meets targets

**Steps**:
1. Process 10 different contract documents
2. Measure metadata extraction accuracy
3. Count obligation coverage percentage
4. Check frequency/deadline accuracy
5. Compare AI vs human corrections
6. Calculate confidence score reliability

**Expected Results**:
- ✅ >80% obligation coverage
- ✅ >80% frequency/deadline accuracy
- ✅ 100% metadata accuracy after human review
- ✅ Confidence scores correlate with accuracy

## Test Execution Checklist

### Pre-Test Setup
- [ ] Docker Compose environment running
- [ ] All services healthy (backend, frontend, AI, database)
- [ ] Sample contracts available for testing
- [ ] Test user accounts created
- [ ] MailHog accessible for email testing
- [ ] Browser developer tools enabled

### During Testing
- [ ] Record all API response times
- [ ] Screenshot each major workflow step
- [ ] Document any errors or unexpected behavior
- [ ] Verify audit logs capture all actions
- [ ] Check database for data consistency
- [ ] Monitor system resource usage

### Post-Test Validation
- [ ] All acceptance criteria met
- [ ] Performance targets achieved
- [ ] Security requirements validated
- [ ] User experience acceptable
- [ ] Data integrity maintained
- [ ] System ready for demo

## Success Criteria

### Functional Requirements ✅
- Complete 15-phase workflow operational
- RBAC with UserProjectPermissions enforced
- AI extraction meets accuracy targets
- Q&A system answers sample queries correctly
- Notification system follows T-14 logic
- Evidence validation workflow complete

### Technical Requirements ✅
- No hardcoded values anywhere in system
- Provider adapters switch via environment variables
- System works with SEED_MODE=none
- Performance acceptable under normal load
- Security measures properly implemented
- Internationalization (English/Arabic) functional

### User Experience Requirements ✅
- Intuitive navigation for all user types
- Responsive design works on mobile/tablet
- Error messages clear and actionable
- Real-time updates provide immediate feedback
- Search functionality fast and accurate
- Dashboards provide valuable insights

## Risk Assessment

### High Risk Items
- AI extraction accuracy on varied document formats
- Performance with large file uploads (>50MB)
- Concurrent user load (>20 simultaneous users)
- Complex query performance in Q&A system

### Medium Risk Items
- Email delivery in production environments
- Browser compatibility (IE, Safari)
- Network connectivity issues
- Storage capacity management

### Low Risk Items
- Basic CRUD operations
- Standard authentication flows
- Static content delivery
- Simple dashboard metrics

## Test Results Summary

*[To be filled during actual test execution]*

### Overall System Health: [PASS/FAIL]
### Critical Workflows: [PASS/FAIL]
### Performance Benchmarks: [PASS/FAIL]
### Security Validation: [PASS/FAIL]
### Acceptance Criteria: [PASS/FAIL]

### Key Findings:
- [To be documented during testing]

### Recommendations:
- [To be provided based on test results]