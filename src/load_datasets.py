import json
from PIL import Image, ImageDraw
import os

# 假設您的 JSON 檔案名稱為 coco-label.json
# 在實際環境中，請確保此檔案與您的 Python 腳本在同一目錄，或者提供正確的路徑
json_file_path = 'dataset/coco-label.json'

try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)
except FileNotFoundError:
    print(f"錯誤：找不到 JSON 檔案 '{json_file_path}'。請確認檔案路徑是否正確。")
    exit()
except json.JSONDecodeError:
    print(f"錯誤：JSON 檔案 '{json_file_path}' 格式不正確。")
    exit()

# 1. 取得第一張影像的資訊
if not coco_data.get('images'):
    print("錯誤：JSON 檔案中沒有 'images' 資訊。")
    exit()

first_image_info = coco_data['images'][0]
image_id = first_image_info['id']
image_file_name = first_image_info['file_name']
image_width = first_image_info['width']
image_height = first_image_info['height']

print(f"第一張圖片資訊：")
print(f"  ID: {image_id}")
print(f"  檔案名稱: {image_file_name}")
print(f"  寬度: {image_width}")
print(f"  高度: {image_height}")

# 2. 載入影像
try:
    # 檢查檔案是否存在
    if not os.path.exists(image_file_name):
        print(f"警告：找不到影像檔案 '{image_file_name}'。將使用一個空白圖片代替進行演示。")
        # 如果找不到圖片，創建一個白色背景的空白圖片作為占位符
        img = Image.new('RGB', (image_width, image_height), color = 'white')
    else:
        img = Image.open(image_file_name).convert("RGB")
except Exception as e:
    print(f"載入影像時發生錯誤 '{image_file_name}': {e}")
    print("將使用一個空白圖片代替進行演示。")
    img = Image.new('RGB', (image_width, image_height), color = 'white')

draw = ImageDraw.Draw(img)

# 3. 找出並繪製與第一張影像相關的 segmentation
annotations_for_image = [anno for anno in coco_data.get('annotations', []) if anno['image_id'] == image_id]

if not annotations_for_image:
    print(f"找不到影像 ID {image_id} 的標註資訊。")
else:
    print(f"\n影像 ID {image_id} 的標註資訊：")
    for i, anno in enumerate(annotations_for_image):
        category_id = anno['category_id']
        category_name = "未知類別"
        for cat in coco_data.get('categories', []):
            if cat['id'] == category_id:
                category_name = cat['name']
                break
        
        print(f"  標註 {i+1}:")
        print(f"    類別 ID: {category_id} (名稱: {category_name})")
        
        if 'segmentation' in anno and anno['segmentation']:
            # COCO segmentation 可以是多個多邊形（針對有孔洞或分離的物件）
            # 這裡我們迭代繪製每一個多邊形
            # segmentation 通常是 [[x1,y1,x2,y2,...], [x1,y1,x2,y2,...]] 或 RLE 格式
            # 此處假設是多邊形座標列表
            segmentation_data = anno['segmentation']
            if isinstance(segmentation_data, list): # 處理多邊形格式
                for seg_points_flat in segmentation_data:
                    if isinstance(seg_points_flat, list) and len(seg_points_flat) > 0:
                        # 將 [x1,y1,x2,y2,...] 轉換為 [(x1,y1), (x2,y2),...]
                        points = []
                        for j in range(0, len(seg_points_flat), 2):
                            points.append((seg_points_flat[j], seg_points_flat[j+1]))
                        
                        # 根據類別給予不同顏色
                        outline_color = "red" # 預設紅色
                        if category_name == "nose":
                            outline_color = "blue"
                        elif category_name == "nostril":
                            outline_color = "green"
                            
                        draw.polygon(points, outline=outline_color, width=3)
                        print(f"      已繪製 '{category_name}' 的分割區域 (顏色: {outline_color})")
                    else:
                        print(f"      警告：標註 {i+1} 的分割數據格式不正確或為空。")
            else:
                # 如果是 RLE 格式，這裡不處理，僅提示
                print(f"      警告：標註 {i+1} 的分割數據可能是 RLE 格式，此腳本未處理。")

        if 'bbox' in anno:
            bbox = anno['bbox'] # [x, y, width, height]
            # 根據類別給予不同顏色
            outline_color_bbox = "red" # 預設紅色
            if category_name == "nose":
                outline_color_bbox = "blue"
            elif category_name == "nostril":
                outline_color_bbox = "green"

            draw.rectangle(
                [(bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3])],
                outline=outline_color_bbox,
                width=2
            )
            print(f"      已繪製 '{category_name}' 的邊界框 (顏色: {outline_color_bbox})")


# 4. 顯示或儲存圖片
output_file_name = "first_image_with_annotations.png"
try:
    img.save(output_file_name)
    print(f"\n已將繪製標註後的第一張圖片儲存為 '{output_file_name}'")
    print("請在您的環境中查看該圖片。")
except Exception as e:
    print(f"儲存圖片時發生錯誤: {e}")

# 如果您在本地環境執行，可以取消註解下面這行來嘗試直接顯示圖片
# img.show()