# Python Discord Automation Script - AI Agent Instructions

## Agent Workflow Overview

The following instructions guide the GPT-4.1 AI Agent for developing, debugging, and enhancing a robust Python script with a feature-rich GUI.  
The goal is to automate sending configurable messages to Discord’s text input field, with user inputs sourced from the GUI or text files.

---

## Agent Task Loop (Order of Operations)

1. **Consult Error Log**
    - At the start of each session or prompt, read the detailed error log.
    - Identify any runtime or syntax errors from the last session.
    - Prioritize addressing and resolving these errors first.

2. **Refactor & Error Correction**
    - Refactor the entire script to improve structure, maintainability, and efficiency.
    - Scan the script for all potential issues.
    - Debug and fix all errors found—syntax, logic, or runtime.

3. **Feature Expansion (Three Features Per Cycle)**
    - For each prompt or "Next" command, add **three** new, fully functional features.
    - Each feature must be implemented on both the backend (logic) and frontend (GUI).
    - Features must be robust, efficient, and user-friendly.

4. **Complete Prompted Request**
    - Address and fulfill any specific user requests or tasks described.

5. **Refactor and Final Error Check**
    - After all changes and additions, refactor the script again.
    - Perform a thorough error scan and fix any remaining issues before considering the task cycle complete.

6. **Detailed Error Logging**
    - Log all detected errors (runtime and syntax) in a dedicated error log file.
    - Each log entry should include:
        - Timestamp
        - Error type (runtime, syntax, etc.)
        - Error message and context
        - Resolution summary (if fixed)
    - Maintain this log as a reference for future sessions and error pattern recognition.

---

## Required Best Practices

- **Validation:** After each change, validate script functionality and ensure all new features work as intended.
- **Consistency:** Always follow Python best practices for code style, structure, and error handling.
- **Documentation:** Comment all new features and complex logic for clarity and maintainability.
- **GUI Design:** Ensure the interface is attractive, intuitive, and provides feedback for all actions and states.
- **Robustness:** All user inputs, file reads, and Discord interactions should be error-tolerant and log issues gracefully.
- **Session Logging:** Keep a summary log of completed tasks, validation results, and metrics (errors fixed, features added, etc.)

---

## Feature Implementation Guidelines

- Backend and frontend logic for each feature must be tightly integrated.
- GUI controls must be bound to backend handlers.
- All new features must be validated with user interaction tests.
- Provide visual and/or audible feedback on all key user actions.
- Ensure all automation is reliable and does not interfere with Discord or other applications.

---

## Session Summary and Metrics

- At the end of each cycle, write a detailed session summary:
    - Tasks completed
    - Features added
    - Errors fixed (with references to error log)
    - Validation results and test outcomes
    - Quantitative metrics (features, errors, time spent, etc.)

---

## Refactoring & Error Correction Reminder

**After every coding task, always perform a final review and refactor the entire script for errors, style, and maintainability.  
Scan for all potential issues, debug, and fix any problems found.  
Update the error log with details of all errors and resolutions.**

---

# 500 Sequential Prompts for VaxityAutoTyper Discord Script Development

## Usage Instructions

### Agent Command System
- Use this file as the single instruction set for GPT-4.1 Agent AI Mode in VSC.
- **"NEXT!" Command**: Delivers exactly 5 prompts at a time from the sequential list
- **Never repeat prompts**: Agent tracks completed prompts and never goes backward unless code was deleted/missing
- **Priority Recovery**: If previous code sections were deleted, edited, or are missing, those prompts get prioritized within the current 5-prompt execution

### Execution Flow on "NEXT!" Command
On every "NEXT!" command, the agent must execute in this exact order:
1. **Review and fix errors first** - Scan for any syntax errors, runtime issues, or broken functionality
2. **Refactor existing code** - Improve structure, efficiency, and maintainability
3. **Add three features** - Implement backend logic + frontend interface for each feature
4. **Complete any user request** - Address specific user requirements or modifications
5. **Refactor again** - Final cleanup and optimization pass
6. **Log all errors and session results** - Document what was completed, issues found, and status

### Prompt Tracking System
- Agent maintains internal counter of completed prompts (1-500)
- Each "NEXT!" execution advances counter by 5
- If code restoration is needed, those prompts take priority within current batch
- Agent reports current progress: "Executing prompts [X-Y] of 500"

## AI Agent Optimization Instructions

**This section is for improving the prompt as it stands, not entering these prompts as they are trying to build a script**

### Current Optimization Status
**Improve Next Prompt**: Focus on adding more specific technical implementation details and error handling patterns. Current prompts need more concrete code examples and specific library recommendations.

### Optimization Guidelines for AI Agent:
1. **Enhance Specificity**: Each prompt should include specific Python libraries, function names, and code patterns
2. **Add Error Context**: Include common error scenarios and specific exception handling for each feature
3. **Include Code Examples**: Provide minimal code snippets or pseudo-code for complex implementations
4. **Specify Dependencies**: List exact package versions and installation commands
5. **Add Validation Steps**: Include specific testing and validation criteria for each prompt
6. **Cross-Reference**: Link related prompts and dependencies between features
7. **Performance Metrics**: Add specific performance benchmarks and optimization targets
8. **Security Considerations**: Include specific security checks and validation patterns
9. **User Experience**: Add specific UI/UX patterns and accessibility requirements
10. **Documentation Standards**: Include specific documentation formats and requirements

### Meta-Improvement Instructions:
- Replace this "Improve Next Prompt" content with updated optimization focus after each review
- Continuously refine prompt specificity and technical depth
- Add new optimization categories as patterns emerge
- Track common failure points and add preventive measures

---

## Phase 1: Project Foundation (Prompts 1-50)

1. Create a new Python project structure with main.py, requirements.txt, and config folders
2. Set up virtual environment requirements for Discord automation project
3. Create main.py with basic imports: tkinter, threading, time, os, sys
4. Add project header comment with version, author, and description
5. Create basic tkinter window class with 800x600 dimensions
6. Add window title "VaxityAutoTyper v0.01" and icon setup
7. Create main application class inheriting from tkinter.Tk
8. Add basic window properties: resizable, center on screen
9. Create requirements.txt with: tkinter, pyautogui, keyboard, threading
10. Add basic error handling wrapper for main application
11. Create config.py file for storing application settings
12. Add basic logging setup with file and console handlers
13. Create utils.py for utility functions
14. Add file_operations.py for text file handling
15. Create discord_handler.py for Discord-specific functions
16. Add basic menu bar with File, Edit, Help options
17. Create main frame layout with left panel and right panel
18. Add status bar at bottom of window
19. Create basic about dialog
20. Add exit confirmation dialog
21. Create file browser dialog for selecting .txt files
22. Add basic file validation for .txt files
23. Create text preview area in right panel
24. Add scrollable text widget for file content display
25. Create control buttons: Start, Stop, Pause, Resume
26. Add progress bar widget for operation status
27. Create settings dialog window
28. Add basic keyboard shortcut handlers
29. Create error message dialog boxes
30. Add file drag-and-drop functionality
31. Create basic text processing functions
32. Add line counter and character counter
33. Create delay settings controls
34. Add typing speed configuration
35. Create output log area
36. Add clear log button
37. Create save settings functionality
38. Add load settings on startup
39. Create backup settings feature
40. Add theme selection (light/dark)
41. Create font selection dialog
42. Add window size persistence
43. Create recent files menu
44. Add file history tracking
45. Create basic help documentation
46. Add tooltips for all controls
47. Create keyboard shortcut help dialog
48. Add version check functionality
49. Create crash report generation
50. Add basic unit test structure

## Phase 2: File Handling & Text Processing (Prompts 51-100)

51. Implement read_text_file function with encoding detection
52. Add support for UTF-8, ASCII, and Windows-1252 encodings
53. Create function to split text into lines
54. Add empty line removal option
55. Implement trim whitespace function
56. Create function to count total lines in file
57. Add function to estimate typing time
58. Implement text preprocessing pipeline
59. Create function to handle special characters
60. Add line length validation
61. Implement text chunking for large files
62. Create function to remove duplicate lines
63. Add text case conversion options
64. Implement find and replace functionality
65. Create function to filter lines by keywords
66. Add line numbering option
67. Implement text encoding conversion
68. Create function to handle different line endings
69. Add BOM (Byte Order Mark) detection and removal
70. Implement file size validation
71. Create function to preview first N lines
72. Add function to get file metadata
73. Implement text statistics calculation
74. Create function to validate file permissions
75. Add function to check file accessibility
76. Implement automatic file backup before processing
77. Create function to handle locked files
78. Add function to monitor file changes
79. Implement batch file processing
80. Create function to merge multiple text files
81. Add function to split large files
82. Implement text format detection
83. Create function to handle CSV files
84. Add function to process markdown files
85. Implement JSON text extraction
86. Create function to handle XML text content
87. Add function to extract text from RTF files
88. Implement clipboard text processing
89. Create function to handle Unicode characters
90. Add function to validate text content
91. Implement text sanitization
92. Create function to handle emoji characters
93. Add function to process URLs in text
94. Implement mention (@username) handling
95. Create function to handle hashtags
96. Add function to process code blocks
97. Implement text formatting preservation
98. Create function to handle nested quotes
99. Add function to escape special Discord characters
100. Implement text length optimization

## Phase 3: Discord Integration & Automation (Prompts 101-150)

101. Create Discord window detection function
102. Add function to find Discord text input field
103. Implement click-to-focus functionality
104. Create function to verify Discord is active
105. Add function to detect Discord channel
106. Implement Discord window state checking
107. Create function to handle Discord notifications
108. Add function to detect typing indicators
109. Implement Discord rate limit detection
110. Create function to handle Discord errors
111. Add function to simulate human typing patterns
112. Implement variable typing speed
113. Create function to add random delays
114. Add function to simulate typing mistakes
115. Implement backspace and correction simulation
116. Create function to handle long messages
117. Add function to split messages at character limit
118. Implement message queuing system
119. Create function to handle message failures
120. Add function to retry failed messages
121. Implement message confirmation detection
122. Create function to handle slow connections
123. Add function to detect Discord updates
124. Implement Discord theme detection
125. Create function to handle Discord shortcuts
126. Add function to avoid Discord hotkeys
127. Implement screen resolution detection
128. Create function to handle multiple monitors
129. Add function to detect Discord position
130. Implement adaptive positioning
131. Create function to handle Discord resizing
132. Add function to detect Discord minimization
133. Implement Discord focus restoration
134. Create function to handle Discord crashes
135. Add function to detect Discord restart
136. Implement Discord process monitoring
137. Create function to handle Discord updates
138. Add function to detect new Discord versions
139. Implement Discord API rate limiting
140. Create function to handle server outages
141. Add function to detect network issues
142. Implement connection retry logic
143. Create function to handle timeouts
144. Add function to detect Discord maintenance
145. Implement graceful error recovery
146. Create function to handle permission errors
147. Add function to detect banned accounts
148. Implement safety checks before sending
149. Create function to validate message content
150. Add function to handle Discord ToS compliance

## Phase 4: User Interface Enhancement (Prompts 151-200)

151. Create modern flat design theme
152. Add custom button styles with hover effects
153. Implement progress bar animations
154. Create custom color scheme
155. Add gradient backgrounds
156. Implement rounded corner styling
157. Create custom icons for buttons
158. Add loading spinners
159. Implement smooth transitions
160. Create custom scrollbars
161. Add tooltip styling
162. Implement dark mode toggle
163. Create light mode styling
164. Add high contrast mode
165. Implement font size scaling
166. Create custom dialog boxes
167. Add animated status indicators
168. Implement tab interface
169. Create collapsible panels
170. Add resizable panes
171. Implement drag-and-drop visual feedback
172. Create custom file browser
173. Add file type icons
174. Implement file preview thumbnails
175. Create custom context menus
176. Add keyboard navigation highlighting
177. Implement focus indicators
178. Create custom input fields
179. Add input validation styling
180. Implement error highlighting
181. Create success indicators
182. Add warning messages styling
183. Implement information tooltips
184. Create help button overlays
185. Add keyboard shortcut displays
186. Implement status bar enhancements
187. Create time remaining display
188. Add speed indicator
189. Implement file counter display
190. Create memory usage indicator
191. Add CPU usage display
192. Implement network status indicator
193. Create Discord connection status
194. Add file processing status
195. Implement queue status display
196. Create log level indicators
197. Add search functionality in logs
198. Implement log filtering
199. Create log export functionality
200. Add log clearing with confirmation

## Phase 5: Advanced Features & Settings (Prompts 201-250)

201. Create comprehensive settings dialog
202. Add typing speed slider with real-time preview
203. Implement custom delay patterns
204. Create random delay range settings
205. Add mistake simulation percentage
206. Implement correction delay settings
207. Create message splitting options
208. Add character limit settings
209. Implement queue management settings
210. Create retry attempt configuration
211. Add timeout settings
212. Implement connection retry settings
213. Create backup settings
214. Add auto-save interval settings
215. Implement log retention settings
216. Create theme customization options
217. Add font selection settings
218. Implement window position saving
219. Create hotkey customization
220. Add notification settings
221. Implement sound effect settings
222. Create performance optimization settings
223. Add memory usage limits
224. Implement CPU usage limits
225. Create network timeout settings
226. Add proxy configuration
227. Implement VPN detection settings
228. Create security settings
229. Add permission level settings
230. Implement user account settings
231. Create profile management
232. Add multiple profile support
233. Implement profile switching
234. Create profile export/import
235. Add profile encryption
236. Implement password protection
237. Create session management
238. Add session timeout settings
239. Implement auto-logout features
240. Create activity monitoring
241. Add usage statistics
242. Implement performance metrics
243. Create error tracking
244. Add crash reporting
245. Implement diagnostic tools
246. Create system information display
247. Add hardware compatibility check
248. Implement software dependency check
249. Create update checking mechanism
250. Add automatic update installation

## Phase 6: Error Handling & Validation (Prompts 251-300)

251. Create comprehensive exception handling framework
252. Add file access error handling
253. Implement permission error recovery
254. Create network error handling
255. Add timeout error recovery
256. Implement Discord connection error handling
257. Create file format validation
258. Add text encoding validation
259. Implement file size validation
260. Create memory usage validation
261. Add disk space checking
262. Implement system resource validation
263. Create input sanitization
264. Add XSS prevention measures
265. Implement SQL injection prevention
266. Create buffer overflow protection
267. Add race condition handling
268. Implement deadlock prevention
269. Create thread safety measures
270. Add atomic operations
271. Implement mutex locks
272. Create semaphore controls
273. Add critical section protection
274. Implement error logging
275. Create error categorization
276. Add error severity levels
277. Implement error reporting
278. Create error recovery strategies
279. Add fallback mechanisms
280. Implement graceful degradation
281. Create retry logic with backoff
282. Add circuit breaker pattern
283. Implement health checks
284. Create monitoring alerts
285. Add diagnostic information
286. Implement debug mode
287. Create verbose logging
288. Add stack trace capture
289. Implement memory leak detection
290. Create performance monitoring
291. Add bottleneck identification
292. Implement optimization suggestions
293. Create usage analytics
294. Add performance benchmarking
295. Implement stress testing
296. Create load testing
297. Add endurance testing
298. Implement security testing
299. Create vulnerability scanning
300. Add penetration testing

## Phase 7: Performance Optimization (Prompts 301-350)

301. Implement multi-threading for file processing
302. Create async/await patterns for I/O operations
303. Add memory pooling for large files
304. Implement lazy loading for text content
305. Create efficient string operations
306. Add buffer management for streaming
307. Implement caching mechanisms
308. Create index structures for fast lookup
309. Add compression for large text files
310. Implement delta compression
311. Create memory-mapped file access
312. Add batch processing optimization
313. Implement parallel processing
314. Create work queue distribution
315. Add load balancing
316. Implement resource pooling
317. Create connection pooling
318. Add thread pool management
319. Implement CPU affinity settings
320. Create NUMA awareness
321. Add cache optimization
322. Implement prefetching strategies
323. Create locality optimization
324. Add memory alignment
325. Implement SIMD optimizations
326. Create vectorized operations
327. Add GPU acceleration support
328. Implement OpenCL integration
329. Create CUDA support
330. Add parallel algorithms
331. Implement lock-free data structures
332. Create wait-free algorithms
333. Add atomic operations optimization
334. Implement memory barriers
335. Create cache-friendly algorithms
336. Add branch prediction optimization
337. Implement profile-guided optimization
338. Create hot path identification
339. Add cold code elimination
340. Implement function inlining
341. Create loop optimization
342. Add tail call optimization
343. Implement constant folding
344. Create dead code elimination
345. Add strength reduction
346. Implement peephole optimization
347. Create register allocation optimization
348. Add instruction scheduling
349. Implement pipeline optimization
350. Create superscalar optimization

## Phase 8: Security & Safety (Prompts 351-400)

351. Implement input validation and sanitization
352. Create secure file handling
353. Add permission checking
354. Implement access control
355. Create audit logging
356. Add security headers
357. Implement encryption at rest
358. Create secure communication
359. Add certificate validation
360. Implement key management
361. Create secure random generation
362. Add password hashing
363. Implement salt generation
364. Create secure session management
365. Add CSRF protection
366. Implement XSS prevention
367. Create SQL injection prevention
368. Add command injection prevention
369. Implement path traversal prevention
370. Create buffer overflow protection
371. Add integer overflow protection
372. Implement format string protection
373. Create memory corruption prevention
374. Add use-after-free protection
375. Implement double-free prevention
376. Create stack overflow protection
377. Add heap overflow protection
378. Implement DEP/NX support
379. Create ASLR support
380. Add stack canaries
381. Implement control flow integrity
382. Create shadow stack
383. Add return address protection
384. Implement indirect call protection
385. Create ROP/JOP mitigation
386. Add code signing verification
387. Implement integrity checking
388. Create tamper detection
389. Add anti-debugging measures
390. Implement anti-reverse engineering
391. Create obfuscation techniques
392. Add runtime protection
393. Implement sandbox execution
394. Create privilege separation
395. Add principle of least privilege
396. Implement defense in depth
397. Create security monitoring
398. Add intrusion detection
399. Implement incident response
400. Create security updates

## Phase 9: Testing & Quality Assurance (Prompts 401-450)

401. Create unit test framework setup
402. Add test for file reading functionality
403. Implement test for text processing
404. Create test for Discord integration
405. Add test for UI components
406. Implement test for error handling
407. Create test for performance metrics
408. Add test for security features
409. Implement test for configuration
410. Create test for logging system
411. Add integration tests
412. Implement system tests
413. Create acceptance tests
414. Add regression tests
415. Implement stress tests
416. Create load tests
417. Add endurance tests
418. Implement security tests
419. Create usability tests
420. Add accessibility tests
421. Implement compatibility tests
422. Create performance tests
423. Add memory leak tests
424. Implement thread safety tests
425. Create race condition tests
426. Add deadlock tests
427. Implement timeout tests
428. Create error recovery tests
429. Add failover tests
430. Implement backup tests
431. Create restore tests
432. Add migration tests
433. Implement upgrade tests
434. Create downgrade tests
435. Add rollback tests
436. Implement data integrity tests
437. Create consistency tests
438. Add validation tests
439. Implement boundary tests
440. Create edge case tests
441. Add negative tests
442. Implement fuzz tests
443. Create mutation tests
444. Add property-based tests
445. Implement mock tests
446. Create stub tests
447. Add dummy tests
448. Implement fake tests
449. Create test data generation
450. Add test environment setup

## Phase 10: Documentation & Deployment (Prompts 451-500)

451. Create comprehensive README.md
452. Add installation instructions
453. Implement usage documentation
454. Create API documentation
455. Add code comments and docstrings
456. Implement inline documentation
457. Create user manual
458. Add troubleshooting guide
459. Implement FAQ section
460. Create changelog documentation
461. Add version history
462. Implement release notes
463. Create migration guide
464. Add upgrade instructions
465. Implement downgrade procedures
466. Create backup procedures
467. Add restore procedures
468. Implement disaster recovery
469. Create monitoring guide
470. Add performance tuning guide
471. Implement security guidelines
472. Create best practices guide
473. Add coding standards
474. Implement review checklist
475. Create deployment guide
476. Add environment setup
477. Implement CI/CD pipeline
478. Create build automation
479. Add test automation
480. Implement deployment automation
481. Create rollback automation
482. Add monitoring automation
483. Implement alerting system
484. Create log aggregation
485. Add metrics collection
486. Implement dashboards
487. Create health checks
488. Add status pages
489. Implement incident management
490. Create change management
491. Add configuration management
492. Implement secret management
493. Create license management
494. Add compliance documentation
495. Implement audit procedures
496. Create final testing checklist
497. Add release preparation
498. Implement version tagging
499. Create distribution packages
500. Add post-deployment verification

**By following this loop, your AI agent will deliver a robust, feature-rich, and error-free Python GUI automation script for Discord.**

---