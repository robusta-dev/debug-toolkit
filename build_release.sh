docker buildx build \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --platform linux/arm64,linux/amd64 \
  --tag robustadev/debug-toolkit:${TAG} \
  --tag us-central1-docker.pkg.dev/genuine-flight-317411/devel/debug-toolkit:${TAG} \
  --push \
  .