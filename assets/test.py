import kagglehub

# Download latest version
path = kagglehub.model_download("google/gemma-3n/transformers/gemma-3n-e2b")

print("Path to model files:", path)