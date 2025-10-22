# Running the Streamlit App - Quick Start

## 30-Second Quick Start

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Install Streamlit (if not already installed)
pip install streamlit pillow

# 3. Run the app
streamlit run app.py
```

Your browser will open to `http://localhost:8501` 🎉

## What You'll See

```
🖼️ Gallery Image Search Agent
*ChatGPT-like interface for intelligent image gallery management*

┌─────────────────────────────────────┐
│  ⚙️ Settings (Sidebar)             │
│  • Model: Gemini 2.5              │
│  • Cache Stats                    │
│  • Clear Conversation             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  💬 Conversation                    │
│  (Chat history displays here)      │
│  📸 Images display below messages  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Chat input field (bottom)         │
│  "Ask about your gallery..."       │
└─────────────────────────────────────┘
```

## Features Available

### 1. Chat Interface
- Ask natural language queries
- Get AI responses
- See conversation history
- Timestamps on messages

### 2. Image Gallery
- View search results
- See image metadata (ID, location, quality, tags)
- Multiple images displayed in grid
- Auto-limits to 6 images per search

### 3. Sidebar Tools
- **Model Info**: Check Gemini 2.5 status
- **Cache Stats**: See cached searches
- **Clear Button**: Reset conversation
- **Settings**: Toggle features
- **Help**: Usage tips

### 4. Multi-Step Workflows
```
User: "Find blurry images"
↓
[Images displayed]
↓
User: "Delete them"
↓
[Agent deletes using cached data]
```

## Example Commands

### Search
```
"Find beach photos"
"Show me sunset images from 2024"
"Find images with landscape tag"
```

### Filter
```
"Show only excellent quality images"
"Find images from Colorado"
"Show me images with sunset tag"
```

### Perform Actions
```
"Delete all blurry images"
"Tag these as favorites"
"Delete the first 3 images"
```

### Get Statistics
```
"Analyze my gallery"
"Show quality distribution"
"How many images total?"
```

## Configuration

### Default Settings
- **Port**: 8501
- **Cache TTL**: 30 minutes
- **Images per search**: 6
- **Layout**: Wide

### Change Port (if 8501 is busy)

```bash
streamlit run app.py --server.port 8502
```

### Custom Config

Create `.streamlit/config.toml`:

```toml
[client]
showErrorDetails = true

[server]
port = 8501
runOnSave = true
```

## Troubleshooting

### Problem: "No module named streamlit"

**Solution**:
```bash
source .venv/bin/activate
pip install streamlit
```

### Problem: "GOOGLE_API_KEY not found"

**Solution**:
```bash
# Make sure .env file exists with:
GOOGLE_API_KEY=your_key_here

# And it's in the project root
ls .env  # Should show the file
```

### Problem: "Address already in use"

**Solution**:
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill the process using 8501
lsof -ti:8501 | xargs kill -9
```

### Problem: App is slow

**Solution**:
- Disable "Show cache details" in sidebar
- Reduce number of images shown (edit app.py, line ~130)
- Check internet connection

### Problem: Images not displaying

**Solution**:
- Make sure search found results
- Check cache is populated (sidebar shows > 0 cached searches)
- Verify image data exists in cache

## File Locations

```
app.py                  ← Main Streamlit app
requirements.txt        ← Dependencies (includes streamlit)
.env                    ← API configuration
STREAMLIT_GUIDE.md      ← Full documentation
RUN_STREAMLIT.md        ← This file
```

## Environment Variables

Required in `.env`:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Optional:

```
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.9
LLM_TOP_K=40
```

## Browser Compatibility

✅ Chrome/Chromium (recommended)
✅ Firefox
✅ Safari
✅ Edge

Recommended: Latest browser version

## Keyboard Shortcuts

- **Enter**: Send message
- **Ctrl+R**: Refresh page
- **Escape**: Close modals

## Tips & Tricks

### 1. Clear History Between Sessions
Use the "Clear Conversation" button in sidebar

### 2. Monitor Cache
Check "Cache Statistics" in sidebar to see how many searches are cached

### 3. View Cache Details
Enable "Show cache details" in settings to see:
- Query used
- Images found
- Cache timestamp

### 4. Multi-Step Operations
```
1. Search for images
2. See results
3. Ask to delete/tag (uses cached results)
4. See confirmation
```

### 5. Complex Queries
The agent can handle multi-part requests:
"Find beach photos from California with sunset tag and excellent quality"

## Performance Tips

1. **First Load**: ~5 seconds (agent initialization)
2. **Subsequent Messages**: ~3-5 seconds (API response)
3. **Image Display**: Instant

## Usage Statistics

In sidebar, you'll see:
- **Cached Searches**: Number of active caches
- **Messages**: Total conversation messages
- **Model**: Gemini 2.5 status

## Dark Mode

Streamlit supports dark mode:
1. Click ⚙️ (bottom right)
2. Select "Dark" theme

## Responsive Design

Works on:
- ✅ Desktop (1920x1080+)
- ✅ Laptop (1280x720+)
- ✅ Tablet (768x1024)
- ✅ Mobile (responsive)

## Server Mode (Headless)

For running on a server:

```bash
streamlit run app.py --server.headless true
```

Then access at: `http://server-ip:8501`

## Docker Deployment

```bash
# Build image
docker build -t gallery-agent .

# Run container
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=your_key \
  gallery-agent
```

## SSH Tunneling (for remote server)

```bash
# Local machine
ssh -L 8501:localhost:8501 user@server

# Then visit http://localhost:8501
```

## Advanced Usage

### Custom Agent Settings

Edit in app.py around line 100:

```python
agent.cache_ttl_minutes = 60  # Change from 30 to 60
```

### Add Custom CSS

Edit the `<style>` section in app.py

### Modify Sidebar

Add more metrics or tools in the sidebar section

## Production Checklist

- [ ] `.env` file configured with API key
- [ ] Requirements installed: `pip install -r requirements.txt`
- [ ] Streamlit installed: `pip install streamlit`
- [ ] Virtual environment activated
- [ ] Test with sample queries
- [ ] Check cache monitoring works
- [ ] Test on different browsers

## Support

For issues:
1. Check troubleshooting section above
2. Review STREAMLIT_GUIDE.md for detailed info
3. Check console for error messages
4. Verify .env configuration

## Next Steps

After launching:
1. Try a search: "Find beach photos"
2. View the results with image gallery
3. Try a delete: "Delete all blurry images"
4. Check cache stats in sidebar
5. Explore settings and help

## Video Tutorial (Manual)

```
Step 1: source .venv/bin/activate
Step 2: pip install streamlit pillow
Step 3: streamlit run app.py
Step 4: Browser opens at http://localhost:8501
Step 5: Start chatting!
```

## Performance Metrics

| Operation | Time |
|-----------|------|
| App load | ~2s |
| Agent init | ~3s |
| Message process | ~3-5s |
| Image display | <100ms |

## Keyboard Accessibility

- Tab through elements
- Enter to select
- Arrow keys to navigate

## Common Workflows

### Search and View
```
1. "Find sunset photos"
2. [Gallery displays with metadata]
3. "Tell me more about the first image"
```

### Search and Delete
```
1. "Find blurry images"
2. [5 images displayed]
3. "Delete all of them"
4. [Confirmation message]
```

### Search and Tag
```
1. "Find beach photos"
2. [3 images displayed]
3. "Tag them as favorites"
4. [Success message]
```

## Summary

✅ Easy to run: `streamlit run app.py`
✅ ChatGPT-like interface
✅ Image gallery display
✅ Real-time statistics
✅ Error handling
✅ Help & settings
✅ Responsive design

**Enjoy! 🎉**

---

**Questions?** See STREAMLIT_GUIDE.md for detailed documentation.
