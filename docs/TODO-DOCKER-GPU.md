# TODO: Docker GPU Support

## Current Status
- ✅ GPU acceleration working in **local backend** (8-10x speedup)
- ❌ GPU acceleration **NOT working in Docker** (Docker can't access GPU)

## Problem
Docker containers cannot access the host's GPU without additional configuration. When running the backend in Docker:
- GPU is not accessible
- Falls back to CPU mode
- Queries take 80-125 seconds instead of 12-15 seconds

## Why This Matters
- **Local backend with GPU:** 12-15 seconds per query
- **Docker backend (CPU only):** 80-125 seconds per query
- **Impact:** 8-10x slower in Docker

## Solution Options

### Option 1: NVIDIA Container Toolkit (Recommended for Production)

**What it does:** Allows Docker containers to access host GPU

**Requirements:**
- NVIDIA GPU with proper drivers installed (✅ we have this)
- NVIDIA Container Toolkit installed on host
- Docker Compose configuration updates

**Setup Steps:**

1. **Install NVIDIA Container Toolkit:**
   ```bash
   # Add NVIDIA package repository
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   
   # Install nvidia-container-toolkit
   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit
   
   # Restart Docker
   sudo systemctl restart docker
   ```

2. **Update docker-compose.yml:**
   ```yaml
   services:
     backend:
       # ... existing config ...
       deploy:
         resources:
           reservations:
             devices:
               - driver: nvidia
                 count: 1
                 capabilities: [gpu]
       environment:
         - NVIDIA_VISIBLE_DEVICES=all
         - NVIDIA_DRIVER_CAPABILITIES=compute,utility
   ```

3. **Test GPU in Docker:**
   ```bash
   docker-compose run backend nvidia-smi
   ```

**Pros:**
- ✅ Proper production solution
- ✅ Works with Docker Compose
- ✅ Supports multiple GPUs
- ✅ Industry standard

**Cons:**
- ❌ Requires system-level installation
- ❌ Adds complexity to deployment
- ❌ May need root/sudo access

### Option 2: Keep Current Hybrid Approach (Current Solution)

**What it does:** Run different components based on workload

**Usage:**
- **Development/Evaluation:** Run backend locally with GPU
  ```bash
  cd backend
  source venv/bin/activate
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

- **Production/Deployment:** Run in Docker (CPU mode is acceptable)
  ```bash
  docker-compose up
  ```

**Pros:**
- ✅ No additional setup needed
- ✅ Already working
- ✅ Simple to understand
- ✅ Best of both worlds

**Cons:**
- ❌ Not fully containerized during development
- ❌ Production deployment will be slower (but may be acceptable)

### Option 3: Cloud GPU Deployment

**What it does:** Deploy to cloud with GPU support

**Options:**
- AWS ECS with GPU instances
- Google Cloud Run with GPU
- Azure Container Instances with GPU

**Pros:**
- ✅ No local GPU configuration needed
- ✅ Scalable
- ✅ Managed infrastructure

**Cons:**
- ❌ Costs money
- ❌ More complex deployment
- ❌ Not for local development

## Recommendation

For this coding exercise:

1. **Keep current hybrid approach** (Option 2):
   - Local backend with GPU for evaluation/testing
   - Docker for deployment demo
   - Document both modes in README

2. **Add NVIDIA Container Toolkit support as optional** (Option 1):
   - Document installation steps
   - Provide docker-compose.gpu.yml as alternative
   - Not required for basic functionality

3. **Document performance trade-offs:**
   - Make it clear that Docker deployment runs in CPU mode
   - Explain that GPU can be enabled with additional setup
   - Show performance benchmarks for both modes

## Implementation Plan

### Phase 1: Documentation (Immediate)
- [ ] Update main README with GPU/CPU performance notes
- [ ] Add DOCKER-GPU.md with detailed setup instructions
- [ ] Update docker-compose.yml with GPU config comments
- [ ] Add note in EVALUATION-REPORT.md about local vs Docker

### Phase 2: Optional GPU Docker Support (If time permits)
- [ ] Create docker-compose.gpu.yml variant
- [ ] Add GPU support installation script
- [ ] Test on WSL2 with NVIDIA Container Toolkit
- [ ] Document in DOCKER-GPU.md

### Phase 3: Production Considerations (Future)
- [ ] Evaluate if GPU needed in production
- [ ] Consider CPU optimization strategies
- [ ] Look into model quantization for faster CPU inference
- [ ] Explore alternative models (lighter weight)

## Notes

- **WSL2 Specifics:** NVIDIA Container Toolkit works on WSL2 with Windows 11
- **Current Performance:** CPU mode is acceptable for demo/low-traffic deployment
- **GPU is Optional:** System works fine without GPU, just slower
- **Evaluation Priority:** Having GPU for evaluation/testing is most important

## References

- [NVIDIA Container Toolkit Documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- [Docker Compose GPU Support](https://docs.docker.com/compose/gpu-support/)
- [WSL2 GPU Support](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)

---

**Status:** POSTPONED - Working hybrid solution in place  
**Priority:** LOW - Not blocking, system works without it  
**Effort:** MEDIUM - Requires system-level changes  
**Decision:** Document current approach, add GPU Docker as optional enhancement
