# Whisper Model Accuracy & Performance Comparison

## Model Size Comparison

| Model | Parameters | Size | Speed | Accuracy | Memory | Best For |
|-------|------------|------|-------|----------|--------|----------|
| **tiny** | 39M | ~39MB | Very Fast | Basic | ~1GB | Quick tests, real-time |
| **base** | 74M | ~74MB | Fast | Fair | ~1GB | General use, decent quality |
| **small** | 244M | ~244MB | Medium | Good | ~2GB | Balanced performance |
| **medium** | 769M | ~769MB | Slow | Very Good | ~5GB | High quality, reasonable speed |
| **large** | 1550M | ~1.5GB | Very Slow | Excellent | ~10GB | Best accuracy |
| **large-v2** | 1550M | ~1.5GB | Very Slow | Excellent+ | ~10GB | Improved accuracy |
| **large-v3** | 1550M | ~1.5GB | Very Slow | Best | ~10GB | Highest accuracy |

## Accuracy Differences

### Real-world Performance (Approximate Word Error Rates):
- **tiny**: ~15-25% WER (many errors, basic transcription)
- **base**: ~10-15% WER (decent for clear speech)
- **small**: ~8-12% WER (good for most content)
- **medium**: ~5-8% WER (very good accuracy)
- **large**: ~3-6% WER (excellent accuracy)
- **large-v2**: ~2-5% WER (excellent+ accuracy)
- **large-v3**: ~2-4% WER (best accuracy)

### Processing Speed on M1 MacBook Pro:
- **tiny**: ~10-20x real-time
- **base**: ~8-15x real-time
- **small**: ~5-10x real-time
- **medium**: ~2-4x real-time
- **large**: ~1-2x real-time
- **large-v2**: ~0.8-1.5x real-time
- **large-v3**: ~0.5-1x real-time

## Recommendations

### Use **tiny** when:
- Testing the script
- Need real-time processing
- Audio quality is very clear
- Accuracy is not critical

### Use **base** when:
- General transcription needs
- Good balance of speed/accuracy
- Clear audio with minimal background noise

### Use **small** when:
- Want good accuracy without long wait times
- Processing many files
- Audio has some background noise

### Use **medium** when:
- High accuracy is important
- Audio has background noise or accents
- Processing time is acceptable (2-4x real-time)

### Use **large-v3** when:
- Maximum accuracy is required
- Audio is complex (multiple speakers, accents, noise)
- Processing time is not a concern
- Professional/business use

## Memory Requirements

- **tiny/base/small**: Work well on 8GB+ RAM
- **medium**: Recommended 16GB+ RAM
- **large/large-v2/large-v3**: Recommended 32GB+ RAM for optimal performance

## When to Choose Medium vs Large-v3

### Choose **medium** if:
- You have 16GB RAM or less
- Processing time matters (2-4x faster than large)
- Audio is relatively clear
- Good accuracy is sufficient

### Choose **large-v3** if:
- You have 32GB+ RAM
- Maximum accuracy is critical
- Audio is complex/noisy
- Processing time is not a concern
- Professional transcription work

## Quick Test

To test different models on your audio:
```bash
# Test with medium model (faster)
./transcribe.sh audio.mp3 --model medium

# Test with large-v3 model (best accuracy)
./transcribe.sh audio.mp3 --model large-v3
```

Compare the results to see if the accuracy difference justifies the extra processing time for your specific use case.
