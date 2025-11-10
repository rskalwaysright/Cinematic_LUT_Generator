from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def extract_palette(image_path, n_colors=6):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((200, 200))
    data = np.array(img).reshape(-1, 3).astype(float) / 255.0
    # KMeans clustering on RGB colors
    kmeans = KMeans(n_clusters=n_colors, random_state=0)
    kmeans.fit(data)
    colors = (kmeans.cluster_centers_ * 255).astype(int)
    return colors

def visualize_palette(colors, save_path='output/preview_palette.png'):
    fig, ax = plt.subplots(figsize=(6, 1))
    ax.imshow([colors/255.0])
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Palette preview saved to {save_path}")
    plt.close(fig)
