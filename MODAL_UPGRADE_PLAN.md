# Modal vLLM Upgrade Plan

## Current Issues
- ❌ vLLM 0.2.7 has tokenizer compatibility issues with Mistral
- ❌ NumPy 2.x compatibility issues (fixed with numpy<2.0)
- ⚠️ Older Python version (3.10 vs 3.12)

## Benefits of Upgrading
- ✅ Fix Mistral tokenizer issues
- ✅ Better NumPy compatibility
- ✅ More model support
- ✅ Performance improvements
- ✅ Better error handling

## Upgrade Options

### Option 1: Conservative Upgrade (Recommended)
Upgrade to vLLM 0.6.x or 0.7.x - newer but still stable:
```python
"vllm>=0.6.0,<0.8.0",
"transformers>=4.40.0",
"torch>=2.1.0",
```

### Option 2: Latest Stable (Like Modal Docs)
Match Modal's official example:
```python
"vllm==0.11.2",
"transformers>=4.40.0",
"torch>=2.1.0",
"python==3.12",
```

### Option 3: Stay Current (Use Compatible Models)
Keep vLLM 0.2.7 but use models that work:
- Qwen 7B Chat ✅
- Llama 2 7B Chat ✅
- Vicuna 7B v1.5 ✅

## Recommendation

**For now:** Use Option 3 - just select compatible models in the dashboard. This works immediately.

**Later:** Upgrade to Option 1 or 2 when you have time to test. The upgrade will:
- Fix Mistral support
- Improve performance
- Add more model options

## Next Steps

If you want to upgrade now, I can:
1. Update `modal_deploy.py` to use newer vLLM
2. Test with Mistral to confirm it works
3. Deploy the updated version

Or we can stick with the current setup and just use Qwen/Llama models that work perfectly!

