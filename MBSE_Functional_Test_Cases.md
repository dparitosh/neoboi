# End-User Functional Test Cases for MBSE Requirements Processing App

## Overview
This document contains comprehensive functional test cases to validate the MBSE requirements processing application. The tests cover document upload, processing, requirements extraction, chat interface, and graph visualization functionality.

**Test Environment Requirements:**
- Neo4j database (local or cloud)
- Ollama service with gemma3:4b model
- Apache Solr search engine
- Python FastAPI backend
- React frontend
- Test documents: ST4000i-OM-01-REV-C.pdf and secondary PDF

**Date:** September 19, 2025
**Version:** 1.0

---

## Test Case 1: Service Startup and Health Check
**Objective:** Verify all required services are running and accessible

**Preconditions:**
- Application installed and configured
- Neo4j database available
- Ollama service running with gemma3:4b model

**Test Steps:**
1. Open command prompt in project directory (`d:\Software\boiSoftware\neoboi`)
2. Run: `python scripts/testing/test-services.bat`
3. Verify all services show "RUNNING" status:
   - ✅ Neo4j connection
   - ✅ Ollama service (gemma3:4b model available)
   - ✅ Apache Solr
   - ✅ Backend API (port 3001)
   - ✅ Frontend (port 3000)

**Expected Results:**
- All services show green/positive status
- No error messages in console output
- Services respond within 30 seconds

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 2: Frontend Application Access
**Objective:** Verify web interface loads and basic navigation works

**Test Steps:**
1. Open web browser
2. Navigate to `http://localhost:3000`
3. Verify page loads completely
4. Check main navigation elements:
   - Graph visualization tab
   - Document upload section
   - Chat interface
   - Search functionality

**Expected Results:**
- Page loads within 10 seconds
- No JavaScript errors in browser console
- All UI elements are visible and clickable
- Fluent Design styling applied correctly

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 3: Document Upload Functionality
**Objective:** Test uploading and processing PDF documents

**Test Steps:**
1. Navigate to Document Upload section
2. Click "Choose Files" or drag & drop your two PDF files:
   - `ST4000i-OM-01-REV-C.pdf` (already attached)
   - Your second PDF document
3. Verify files appear in "Selected Files" list
4. Click "Upload" button
5. Monitor upload progress

**Expected Results:**
- Files accepted without errors
- Upload progress shown
- Success message displayed
- Files processed within 2 minutes each
- No file size or format errors

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 4: Document Processing Validation
**Objective:** Verify documents are processed and content extracted

**Test Steps:**
1. After upload completes, check processing results
2. Navigate to processed documents list
3. Verify both PDFs appear in the list
4. Click on each document to view details
5. Check extracted content includes:
   - Text content from PDF
   - Document metadata
   - Processing status

**Expected Results:**
- Both documents show "processed successfully"
- Text content extracted from PDFs
- No processing errors
- Document metadata captured (filename, size, etc.)

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 5: Requirements Extraction
**Objective:** Test LLM-powered requirements extraction from documents

**Test Steps:**
1. For each uploaded document, use the "Analyze Document" feature
2. Verify LLM analysis includes:
   - Document summary
   - Key entities identified
   - Requirements extracted
   - Technical specifications
3. Check that requirements are properly categorized

**Expected Results:**
- LLM generates coherent analysis
- Requirements clearly identified and extracted
- Technical content properly understood
- Analysis completes within 30 seconds

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 6: Knowledge Graph Population
**Objective:** Verify requirements are added to Neo4j knowledge graph

**Test Steps:**
1. Navigate to Graph Visualization tab
2. Check that new nodes appear for:
   - Document nodes
   - Requirements nodes
   - Entity nodes
   - Relationship connections
3. Verify graph shows relationships between requirements

**Expected Results:**
- Graph updates with new content
- Requirements appear as connected nodes
- Relationships show traceability links
- Graph renders within 10 seconds

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 7: Chat Interface - Requirements Querying
**Objective:** Test natural language querying of requirements

**Test Steps:**
1. Open Chat interface
2. Ask specific questions about the uploaded documents:
   - "What are the main requirements in the ST4000i document?"
   - "Compare requirements between the two documents"
   - "What are the technical specifications mentioned?"
3. Verify responses are:
   - Relevant to the documents
   - Based on extracted content
   - Properly formatted

**Expected Results:**
- Chat responds to queries within 10 seconds
- Answers are accurate and relevant
- Responses include specific details from PDFs
- No generic or irrelevant answers

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 8: Requirements Generation
**Objective:** Test AI-powered generation of new requirements

**Test Steps:**
1. In Chat interface, ask for new requirements:
   - "Generate additional requirements for system reliability"
   - "Create requirements for data security based on the documents"
   - "Suggest requirements for system integration"
2. Verify generated requirements are:
   - Consistent with existing requirements
   - Properly formatted
   - Technically sound

**Expected Results:**
- New requirements generated successfully
- Requirements follow proper format
- Content aligns with document context
- Generation completes within 15 seconds

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 9: Search Functionality
**Objective:** Test full-text search across processed documents

**Test Steps:**
1. Use Search interface to query:
   - Specific technical terms from PDFs
   - Requirements keywords
   - System specifications
2. Verify search results show:
   - Relevant document sections
   - Highlighted search terms
   - Accurate matches

**Expected Results:**
- Search returns relevant results
- Results highlight matching content
- Search completes within 5 seconds
- No false positives or misses

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 10: Graph Query and Analysis
**Objective:** Test advanced graph queries for requirements analysis

**Test Steps:**
1. Use Graph search to find:
   - All requirements related to a specific component
   - Dependencies between requirements
   - Requirements traceability
2. Test graph expansion features
3. Verify relationship visualization

**Expected Results:**
- Graph queries return correct results
- Relationships properly visualized
- Graph interactions work smoothly
- Complex queries execute within 10 seconds

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 11: Cross-Document Analysis
**Objective:** Test analysis across multiple documents

**Test Steps:**
1. Ask Chat to compare requirements between documents
2. Request identification of:
   - Conflicting requirements
   - Missing requirements
   - Complementary requirements
3. Verify analysis considers both documents

**Expected Results:**
- Cross-document analysis works
- Relationships between documents identified
- Analysis is comprehensive and accurate
- No document isolation issues

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 12: Export and Reporting
**Objective:** Test data export capabilities

**Test Steps:**
1. Export processed requirements
2. Export graph data
3. Generate summary reports
4. Verify export formats are usable

**Expected Results:**
- Export functions work without errors
- Data formats are correct
- Files download successfully
- Content is complete and accurate

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 13: Performance and Scalability
**Objective:** Verify application performance with real data

**Test Steps:**
1. Time various operations:
   - Document upload (< 2 minutes)
   - Requirements extraction (< 30 seconds)
   - Chat responses (< 10 seconds)
   - Graph rendering (< 10 seconds)
2. Test with both documents loaded simultaneously

**Expected Results:**
- All operations complete within expected timeframes
- No performance degradation with multiple documents
- Memory usage remains reasonable
- Application remains responsive

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 14: Error Handling
**Objective:** Test application robustness

**Test Steps:**
1. Try uploading invalid file types
2. Test with corrupted PDFs
3. Submit malformed queries
4. Test network interruptions during processing

**Expected Results:**
- Graceful error messages displayed
- Application recovers from errors
- No crashes or data corruption
- Clear user guidance for error resolution

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Case 15: Data Persistence
**Objective:** Verify data is properly stored and retrievable

**Test Steps:**
1. Upload documents and process them
2. Restart all services
3. Verify documents and requirements still accessible
4. Check that chat history and analysis persist

**Expected Results:**
- All data persists across restarts
- No data loss during service cycling
- Graph data remains intact
- Processing results are cached appropriately

**Pass/Fail Criteria:** ☐ Pass ☐ Fail
**Execution Time:** ____ seconds
**Notes:** __________________________

---

## Test Execution Guidelines

### Prerequisites for Testing:
1. All services running (Neo4j, Ollama, Solr, Backend, Frontend)
2. Two PDF documents ready for upload
3. Web browser with JavaScript enabled
4. Sufficient system resources (4GB+ RAM recommended)

### Test Data:
- Primary test document: `ST4000i-OM-01-REV-C.pdf`
- Secondary test document: Your second PDF
- Expected content: Technical specifications, requirements, procedures

### Success Criteria:
- ✅ All test cases pass without critical errors
- ✅ Core functionality works end-to-end
- ✅ Performance meets expectations
- ✅ User experience is smooth and intuitive

### Reporting:
For each test case, record:
- Pass/Fail status
- Execution time
- Any errors encountered
- Screenshots of key results
- Performance metrics

---

## Test Results Summary

| Test Case | Status | Execution Time | Notes |
|-----------|--------|----------------|-------|
| TC-01: Service Startup | ☐ | ____ | _____ |
| TC-02: Frontend Access | ☐ | ____ | _____ |
| TC-03: Document Upload | ☐ | ____ | _____ |
| TC-04: Document Processing | ☐ | ____ | _____ |
| TC-05: Requirements Extraction | ☐ | ____ | _____ |
| TC-06: Knowledge Graph | ☐ | ____ | _____ |
| TC-07: Chat Querying | ☐ | ____ | _____ |
| TC-08: Requirements Generation | ☐ | ____ | _____ |
| TC-09: Search Functionality | ☐ | ____ | _____ |
| TC-10: Graph Query | ☐ | ____ | _____ |
| TC-11: Cross-Document Analysis | ☐ | ____ | _____ |
| TC-12: Export/Reporting | ☐ | ____ | _____ |
| TC-13: Performance | ☐ | ____ | _____ |
| TC-14: Error Handling | ☐ | ____ | _____ |
| TC-15: Data Persistence | ☐ | ____ | _____ |

**Overall Test Result:** ☐ Pass ☐ Fail ☐ Partial
**Total Test Cases:** 15
**Passed:** ____
**Failed:** ____
**Pass Rate:** ____%

**Test Execution Date:** ________________
**Tester:** ________________
**Environment:** ________________

---

## Known Issues and Recommendations

### Issues Found:
1. ________________
2. ________________
3. ________________

### Recommendations:
1. ________________
2. ________________
3. ________________

---

## Appendix: Test Environment Setup

### Required Software:
- Node.js 16+
- Python 3.8+
- Java 11+ (for Solr)
- Neo4j database
- Ollama with gemma3:4b model

### Configuration Files:
- `.env.local` - Environment variables
- `config/.env.local` - Service configuration

### Service Ports:
- Frontend: 3000
- Backend: 3001
- Solr: 8983
- Neo4j: 7687
- Ollama: 11434

### Startup Commands:
```bash
# Test all services
python scripts/testing/test-services.bat

# Start individual services
./scripts/services/start-all-complete.bat

# Check service status
./scripts/services/status-complete.bat
```</content>
<parameter name="filePath">d:\Software\boiSoftware\neoboi\MBSE_Functional_Test_Cases.md