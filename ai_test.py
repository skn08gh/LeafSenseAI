from transformers import pipeline
classifier = pipeline("image-classification",model="google/vit-base-patch16-224")
result = classifier("https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/beignets-task-guide.png")
print(result)