# Debug System Documentation

## Overview

The debug system provides comprehensive logging and callback tracking for test execution. It captures all key events during test runs and stores them in JSON format for analysis.

## Features

- ✅ **JSON-based Configuration** - Configure debug settings via `assets/config/debug_config.json`
- ✅ **Event Callbacks** - Track all test lifecycle events
- ✅ **JSON Export** - Export logs as formatted JSON
- ✅ **File Saving** - Save logs to device storage
- ✅ **Debug Screen** - View logs in-app with summary statistics
- ✅ **Console Logging** - Optional console output for real-time debugging

## Configuration

Edit `assets/config/debug_config.json` to control debug behavior:

```json
{
  "enabled": true,
  "logLevel": "verbose",
  "logToFile": true,
  "logToConsole": true,
  "callbacks": {
    "onTestStart": true,
    "onQuestionLoad": true,
    "onQuestionDisplay": true,
    "onAnswerSelect": true,
    "onAnswerSubmit": true,
    "onQuestionChange": true,
    "onTestComplete": true,
    "onScoreCalculate": true,
    "onLevelUpdate": true,
    "onPerformanceUpdate": true
  },
  "includeTimestamps": true,
  "includeUserData": false,
  "includeQuestionData": true,
  "includePerformanceMetrics": true,
  "maxLogEntries": 1000,
  "exportFormat": "json"
}
```

### Configuration Options

- **enabled**: Enable/disable debug logging
- **logLevel**: Logging verbosity level
- **logToFile**: Automatically save logs to file after test completion
- **logToConsole**: Print logs to console in real-time
- **callbacks**: Enable/disable specific event callbacks
- **includeQuestionData**: Include full question details in logs
- **includePerformanceMetrics**: Include performance statistics
- **maxLogEntries**: Maximum number of log entries to keep in memory

## Callbacks

### Test Lifecycle

1. **onTestStart** - Fired when test session begins
   - Session type, total questions, user info

2. **onQuestionLoad** - Fired when questions are loaded
   - Question count, IDs, topics, difficulties, source

3. **onQuestionDisplay** - Fired when a question is shown
   - Question details, index, progress

4. **onAnswerSelect** - Fired when user selects an answer
   - Selected answer, correct answer, correctness

5. **onAnswerSubmit** - Fired when answer is submitted
   - Answer details, correctness, time spent

6. **onQuestionChange** - Fired when navigating between questions
   - From/to indices, direction

7. **onTestComplete** - Fired when test finishes
   - Final score, level, performance metrics

### Scoring & Performance

8. **onScoreCalculate** - Fired during score calculation
   - Attempts data, calculated score, level

9. **onLevelUpdate** - Fired when user level changes
   - Old/new level, score

10. **onPerformanceUpdate** - Fired when topic performance updates
    - Topic ID, attempts, correct, mastery percentage

## Usage

### Accessing Debug Logs

1. **Via Settings Screen**:
   - Go to Settings → Developer → Debug Logs
   - View logs, export JSON, or save to file

2. **Programmatically**:
   ```dart
   // Get logs
   final logs = DebugService.instance.getLogs();
   
   // Export as JSON
   final json = await DebugService.instance.exportLogs();
   
   // Save to file
   final file = await DebugService.instance.saveLogsToFile();
   
   // Get summary
   final summary = DebugService.instance.getSummary();
   ```

### Log Format

Each log entry follows this structure:

```json
{
  "event": "test",
  "action": "start",
  "timestamp": "2024-11-27T10:30:00.000Z",
  "data": {
    "sessionType": "placement",
    "totalQuestions": 50,
    "userId": 1,
    "userLevel": "beginner",
    "metadata": {}
  }
}
```

### Example Log Output

```json
{
  "exportedAt": "2024-11-27T10:35:00.000Z",
  "totalEntries": 25,
  "config": { ... },
  "logs": [
    {
      "event": "test",
      "action": "start",
      "timestamp": "2024-11-27T10:30:00.000Z",
      "data": {
        "sessionType": "placement",
        "totalQuestions": 50
      }
    },
    {
      "event": "question",
      "action": "load",
      "timestamp": "2024-11-27T10:30:01.000Z",
      "data": {
        "source": "database",
        "count": 50,
        "questionIds": ["q_001", "q_002", ...]
      }
    },
    {
      "event": "question",
      "action": "display",
      "timestamp": "2024-11-27T10:30:02.000Z",
      "data": {
        "questionIndex": 0,
        "totalQuestions": 50,
        "progress": 0.02
      }
    }
  ]
}
```

## Debug Screen Features

The debug screen provides:

- **Summary Statistics**: Total entries, event counts, enabled status
- **Log List**: Chronological list of all logged events
- **Export Options**:
  - Copy JSON to clipboard
  - Save to file
  - Clear logs

## Integration

The debug service is automatically initialized in `main.dart` and integrated into:

- `TestScreen` - All test lifecycle events
- `ScoringService` - Score calculations
- `PerformanceRepository` - Performance updates

## Best Practices

1. **Disable in Production**: Set `enabled: false` for production builds
2. **Limit Log Entries**: Set appropriate `maxLogEntries` to prevent memory issues
3. **Selective Callbacks**: Enable only needed callbacks to reduce overhead
4. **Regular Cleanup**: Clear logs periodically to free memory
5. **Export Before Clearing**: Always export logs before clearing

## Troubleshooting

### Logs Not Appearing

1. Check `debug_config.json` exists and `enabled: true`
2. Verify asset is included in `pubspec.yaml`
3. Check console for initialization errors

### Performance Issues

1. Reduce `maxLogEntries`
2. Disable unnecessary callbacks
3. Set `includeQuestionData: false` if not needed
4. Disable `logToConsole` in production

### File Not Saving

1. Check app has storage permissions
2. Verify `logToFile: true` in config
3. Check device storage space

## Future Enhancements

- [ ] Filter logs by event type
- [ ] Search functionality
- [ ] Log compression
- [ ] Remote log upload (optional)
- [ ] Performance profiling integration
- [ ] Custom callback hooks

