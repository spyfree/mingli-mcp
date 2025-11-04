# Release Notes v1.0.9

**Release Date**: 2025-11-04
**Build**: Hotfix Release
**Focus**: Smithery Scanner Compatibility + Quality Score Improvements

---

## 🎯 Purpose

This release includes the quality improvements from v1.0.8 PLUS fixes for Smithery's automated scanner to properly detect the server's tools and capabilities.

## ✨ What's New

### Scanner Compatibility Fix
- ✅ **Added `package.json`** with MCP transport metadata
- ✅ Explicitly declares this is a **stdio-based server** (not HTTP)
- ✅ Provides Smithery scanner with proper invocation method: `uvx mingli-mcp`

### Quality Score Improvements (from v1.0.8)
- ✅ **True zero-configuration** (+15 points)
  - Moved `fastapi` and `uvicorn` to optional dependencies `[http]`
  - stdio mode now fully independent with minimal dependencies
- ✅ **Complete tool documentation** (+12 points)
  - Fixed `list_fortune_systems` inputSchema with explicit description
  - All 7 tools now have proper documentation

## 📊 Quality Score Progression

| Version | Score | Change | Notes |
|---------|-------|--------|-------|
| v1.0.7  | 62/100 | Baseline | Before improvements |
| v1.0.8  | 89/100 | +27 | Quality improvements |
| v1.0.9  | 89/100 | +0 | Scanner compatibility fix |

**Expected Final Score**: 89/100 🎉

## 🔧 Technical Changes

### File Changes
```
config.py         - Version bump to 1.0.9
package.json      - NEW: MCP metadata for Smithery
pyproject.toml    - Version bump to 1.0.9
```

### package.json Content
```json
{
  "mcp": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["mingli-mcp"],
    "capabilities": {
      "tools": true,
      "prompts": true,
      "resources": true
    }
  }
}
```

## 📦 Installation

### Recommended (via uvx)
```bash
uvx mingli-mcp
```

### Via pip (basic)
```bash
pip install mingli-mcp
```

### With HTTP support (optional)
```bash
pip install mingli-mcp[http]
```

## 🚀 Deployment Status

✅ **PyPI**: https://pypi.org/project/mingli-mcp/1.0.9/
✅ **GitHub**: https://github.com/spyfree/mingli-mcp/releases
🔄 **Smithery**: Automatic re-scan in progress (2-3 minutes)

## 🔍 What to Expect

### Smithery Scanner Behavior
1. **PyPI Detection**: Smithery will detect v1.0.9 from PyPI
2. **Metadata Reading**: Reads `package.json` for transport info
3. **Tool Scanning**: Invokes `uvx mingli-mcp` via stdio
4. **Quality Analysis**: Analyzes code for quality improvements
5. **Score Update**: Updates quality score to ~89/100

### Timeline
- **0-2 min**: PyPI indexing complete
- **2-5 min**: Smithery automatic re-scan
- **5-10 min**: Quality score visible on Smithery page

## ✅ Verification Steps

1. **Check PyPI deployment**:
   ```bash
   pip index versions mingli-mcp
   # Should show: mingli-mcp (1.0.9)
   ```

2. **Test local installation**:
   ```bash
   uvx mingli-mcp
   # Should start without errors
   ```

3. **Verify tools work**:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | uvx mingli-mcp
   # Should return list of 7 tools
   ```

4. **Check Smithery page** (after 5-10 min):
   - Visit: https://server.smithery.ai/@spyfree/mingli-mcp
   - Quality score should show ~89/100
   - Tools tab should list all 7 tools
   - Scanner status should be "✅ Success"

## 🐛 Known Issues

### Resolved
- ✅ Scan failed with HTTP timeout → Fixed with package.json
- ✅ HTTP dependencies required for stdio mode → Moved to optional

### Open Issues
- None at this time

## 📝 Breaking Changes

**None**. This is a fully backward-compatible release.

## 🔄 Migration Guide

No migration needed. Simply upgrade:

```bash
# For uvx users (automatic)
uvx mingli-mcp  # Always uses latest

# For pip users
pip install --upgrade mingli-mcp
```

## 🙏 Acknowledgments

Thanks to:
- Smithery team for the quality scoring system
- MCP community for protocol specifications
- Users who reported the scanner issue

## 📚 Additional Resources

- [README.md](README.md) - Full documentation
- [CHANGELOG_v1.0.8.md](CHANGELOG_v1.0.8.md) - Quality improvements details
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Smithery Documentation](https://smithery.ai/docs)

---

**Questions or Issues?**
Open an issue at: https://github.com/spyfree/mingli-mcp/issues
