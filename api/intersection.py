import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 12))  
ax.set_xlim(0, 200)  # length
ax.set_ylim(0, 300)  # height

ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

lane_width = 5  # fixed width for lane lines

# lanes
vertical_lanes_per_direction = 5  
horizontal_lanes_per_direction = 3 

vertical_road_width = vertical_lanes_per_direction * 2 * lane_width 
horizontal_road_width = horizontal_lanes_per_direction * 2 * lane_width  

# intersection
intersection_center_x = 100  
intersection_center_y = 150  

# grass
ax.fill_betweenx([0, 300], 0, (200 - vertical_road_width) / 2, color='green', zorder=0)  # left
ax.fill_betweenx([0, 300], 200 - (200 - vertical_road_width) / 2, 200, color='green', zorder=0)  # right
ax.fill_between([0, 200], 0, (300 - horizontal_road_width) / 2, color='green', zorder=0)  # bottom
ax.fill_between([0, 200], 300 - (300 - horizontal_road_width) / 2, 300, color='green', zorder=0)  # top

# vertical road - black
ax.fill_betweenx([0, 300], (200 - vertical_road_width) / 2, 200 - (200 - vertical_road_width) / 2, color='black', zorder=1)

# horizontal road - black
ax.fill_between([100, 200], (300 - horizontal_road_width) / 2, 300 - (300 - horizontal_road_width) / 2, color='black', zorder=1)

# intersection box
intersection_x_min = intersection_center_x - vertical_road_width / 2
intersection_x_max = intersection_center_x + vertical_road_width / 2
intersection_y_min = intersection_center_y - horizontal_road_width / 2
intersection_y_max = intersection_center_y + horizontal_road_width / 2

# vertical raod - dashed lane dividers
for i in range(1, vertical_lanes_per_direction):  
    lane_x_left = intersection_center_x - i * lane_width
    lane_x_right = intersection_center_x + i * lane_width
    
    ax.plot([lane_x_left, lane_x_left], [0, intersection_y_min], linestyle='dashed', color='white', linewidth=1.5, zorder=2)
    ax.plot([lane_x_left, lane_x_left], [intersection_y_max, 300], linestyle='dashed', color='white', linewidth=1.5, zorder=2)
    
    ax.plot([lane_x_right, lane_x_right], [0, intersection_y_min], linestyle='dashed', color='white', linewidth=1.5, zorder=2)
    ax.plot([lane_x_right, lane_x_right], [intersection_y_max, 300], linestyle='dashed', color='white', linewidth=1.5, zorder=2)

# horizontal raod - dashed lane dividers
for i in range(1, horizontal_lanes_per_direction):  
    lane_y_bottom = intersection_center_y - i * lane_width
    lane_y_top = intersection_center_y + i * lane_width
    
    ax.plot([intersection_x_max, 200], [lane_y_bottom, lane_y_bottom], linestyle='dashed', color='white', linewidth=1.5, zorder=2)
    ax.plot([intersection_x_max, 200], [lane_y_top, lane_y_top], linestyle='dashed', color='white', linewidth=1.5, zorder=2)

# yellow center lines
ax.plot([intersection_center_x, intersection_center_x], [0, intersection_y_min], linestyle='solid', color='yellow', linewidth=3, zorder=3)  
ax.plot([intersection_center_x, intersection_center_x], [intersection_y_max, 300], linestyle='solid', color='yellow', linewidth=3, zorder=3)  

ax.plot([intersection_x_max, 200], [intersection_center_y, intersection_center_y], linestyle='solid', color='yellow', linewidth=3, zorder=3)  

# pedestrian crossing


# signs
import matplotlib.patches as patches
import matplotlib.transforms as transforms

scale = 0.7
sign_width = 20 * scale
sign_height = 8 * scale
pole_height = 6 * scale
pole_width = 1.5 * scale

sign_positions = [
    (55, 280, "관악로"),  
    (180, 175, "낙성대로") 
]

for sign_x, sign_y, text in sign_positions:
    transform = transforms.Affine2D().rotate_deg_around(sign_x + sign_width / 2, sign_y + sign_height / 2, 90) + ax.transData

    sign = patches.FancyBboxPatch(
        (sign_x, sign_y), sign_width, sign_height,
        boxstyle="round,pad=0.2", edgecolor="white",
        facecolor="black", linewidth=0.5, zorder=4,
        transform=transform  # Apply rotation
    )
    ax.add_patch(sign)

    plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'Nanum Gothic', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False

    ax.text(sign_x + sign_width / 2, sign_y + sign_height / 2, text, 
            fontsize=int(10 * scale), color="white",
            ha="center", va="center", fontweight="extra bold", zorder=5,
            rotation=90)  

    pole = patches.Rectangle(
        (sign_x + sign_width / 2 - pole_width / 2, sign_y - pole_height), 
        pole_width, pole_height, facecolor="lightgray", edgecolor="black",
        zorder=3, transform=transform)
    ax.add_patch(pole)

# scaling
ax.set_aspect(1)  

# color similarity function
def is_similar_color(pixel, targets, tol):
    r, g, b, *alpha = pixel
    for target in targets:
        if (
            abs(r - target[0]) <= tol and
            abs(g - target[1]) <= tol and
            abs(b - target[2]) <= tol
        ):
            return True
    return False

# modifies color
def apply_color_variation(img, target_color, new_color, tolerance=50):
    pixels = list(img.getdata())
    
    new_pixels = [
        (new_color + (pixel[3],)) if is_similar_color(pixel, [target_color], tolerance) else pixel
        for pixel in pixels
    ]
    
    img.putdata(new_pixels)
    return img

# truck bed
def modify_truck_bed(img):
    truck_bed_lines_yellow = [
        (255, 236, 38),  
        (255, 239, 77), 
        (209, 196, 31)   
    ]
    truck_bed_background = (255, 236, 38)  
    black_replacement = (65, 65, 65)  
    dark_gray_replacement = (180, 180, 180)  
    
    tolerance_yellow_lines = 20
    tolerance_truck_bed = 30
    
    pixels = list(img.getdata())
    
    modified_pixels = []
    for pixel in pixels:
        if is_similar_color(pixel, [truck_bed_background], tolerance_truck_bed):
            modified_pixels.append(dark_gray_replacement + (pixel[3],))  
        elif is_similar_color(pixel, truck_bed_lines_yellow, tolerance_yellow_lines):
            modified_pixels.append(black_replacement + (pixel[3],)) 
        else:
            modified_pixels.append(pixel)
    
    img.putdata(modified_pixels)
    return img

# color options
color_variants = {
    1: (210, 180, 140),   # tan
    2: (0, 0, 139),       # dark blue
    3: (255, 255, 255),   # white
    4: (80, 80, 80),      # dark gray
    5: (200, 0, 00),      # red
    6: (190, 190, 190)    # light gray
}

# bike
def draw_bike(ax, color_number, x, y, scale, rotation_angle=0):
    bike_path = "./static/cycle.png"  
    bike_original_color1 = (170, 1, 0) 
    bike_original_color2 = (255, 42, 42)
    bike_original_color3 = (113, 4, 5)
    body_color = color_variants.get(color_number, (170, 1, 0))
    
    img = Image.open(bike_path).convert("RGBA")
    modified_bike = apply_color_variation(img, bike_original_color1, body_color)
    modified_bike = apply_color_variation(img, bike_original_color2, body_color)
    modified_bike = apply_color_variation(img, bike_original_color3, body_color)

    new_size = (int(modified_bike.width * scale), int(modified_bike.height * scale))
    modified_bike = modified_bike.resize(new_size, Image.LANCZOS)

    if rotation_angle in [90, 180, 270]:
        modified_bike = modified_bike.rotate(rotation_angle, expand=True)

    if rotation_angle in [90, 270]:
        img_extent = [x, x + new_size[1] / 5, y, y + new_size[0] / 5] 
    else: 
        img_extent = [x, x + new_size[0] / 5, y, y + new_size[1] / 5]

    ax.imshow(modified_bike, extent=img_extent, zorder=5)

# sedan
def draw_sedan(ax, color_number, x, y, scale, rotation_angle=0):
    sedan_path = "./static/sedan.png"  
    sedan_original_color = (165, 42, 42) 
    body_color = color_variants.get(color_number, (165, 42, 42))
    
    img = Image.open(sedan_path).convert("RGBA")
    modified_sedan = apply_color_variation(img, sedan_original_color, body_color)

    new_size = (int(modified_sedan.width * scale), int(modified_sedan.height * scale))
    modified_sedan = modified_sedan.resize(new_size, Image.LANCZOS)

    if rotation_angle in [90, 180, 270]:
        modified_sedan = modified_sedan.rotate(rotation_angle, expand=True)

    if rotation_angle in [90, 270]:
        img_extent = [x, x + new_size[1] / 5, y, y + new_size[0] / 5] 
    else: 
        img_extent = [x, x + new_size[0] / 5, y, y + new_size[1] / 5]

    ax.imshow(modified_sedan, extent=img_extent, zorder=5)

# suv
def draw_suv(ax, color_number, x, y, scale, rotation_angle=0):
    suv_path = "./static/suv.png"  
    suv_original_color = (50, 50, 150)  
    body_color = color_variants.get(color_number, (50, 50, 150))
    
    img = Image.open(suv_path).convert("RGBA")
    modified_suv = apply_color_variation(img, suv_original_color, body_color)

    new_size = (int(modified_suv.width * scale), int(modified_suv.height * scale))
    modified_suv = modified_suv.resize(new_size, Image.LANCZOS)

    if rotation_angle in [90, 180, 270]:
        modified_suv = modified_suv.rotate(rotation_angle, expand=True)

    if rotation_angle in [90, 270]:
        img_extent = [x, x + new_size[1] / 5, y, y + new_size[0] / 5] 
    else: 
        img_extent = [x, x + new_size[0] / 5, y, y + new_size[1] / 5]

    ax.imshow(modified_suv, extent=img_extent, zorder=5)

# truck
def draw_truck(ax, color_number, x, y, scale, rotation_angle=0):
    truck_path = "./static/truck.png" 
    truck_original_color = (139, 69, 19) 
    body_color = color_variants.get(color_number, (139, 69, 19))
    
    img = Image.open(truck_path).convert("RGBA")
    modified_truck = modify_truck_bed(img)
    modified_truck = apply_color_variation(modified_truck, truck_original_color, body_color)
    
    new_size = (int(modified_truck.width * scale), int(modified_truck.height * scale))
    modified_truck = modified_truck.resize(new_size, Image.LANCZOS)

    if rotation_angle in [90, 180, 270]:
        modified_truck = modified_truck.rotate(rotation_angle, expand=True)

    if rotation_angle in [90, 270]:
        img_extent = [x, x + new_size[1] / 5, y, y + new_size[0] / 5] 
    else: 
        img_extent = [x, x + new_size[0] / 5, y, y + new_size[1] / 5]
     
    ax.imshow(modified_truck, extent=img_extent, zorder=5)

# downloading sample data
file_path = "./data/intersection.csv"
df = pd.read_csv(file_path, encoding="utf-8")

age_bins = [0, 25, 35, 45, 55, 65, 100]  # min: 17, max: 85
age_labels = [1, 2, 3, 4, 5, 6]
df["Age Group"] = pd.cut(df["나이"], bins=age_bins, labels=age_labels, right=False)
df["Age Group"] = df["Age Group"].astype(int)
df["Color"] = df["Age Group"].map(color_variants)

"""
# drawing cars
draw_bike(ax, color_number=2, x=55, y=85, scale=0.50)
draw_sedan(ax, color_number=2, x=45, y=85, scale=0.50) 
draw_suv(ax, color_number=2, x=50, y=85, scale=0.50) 
draw_truck(ax, color_number=2, x=55, y=85, scale=0.50)

""" 

def draw_vehicle(initial_x, x_shift, initial_y, y_shift, age_group, alc_group, index, angle):
    if (alc_group == 0 or alc_group is None):
        draw_bike(ax, color_number=age_group, x=initial_x + (index*x_shift), y=initial_y + (index*y_shift), scale=0.1, rotation_angle = angle)
    elif (alc_group > 0.01 and alc < 0.1):
        draw_sedan(ax, color_number=age_group, x=initial_x + (index*x_shift), y=initial_y + (index*y_shift), scale=0.5, rotation_angle = angle)
    elif (alc_group < 0.2):
        draw_suv(ax, color_number=age_group, x=initial_x + (index*x_shift), y=initial_y + (index*y_shift), scale=0.5, rotation_angle = angle)
    elif (alc_group < 0.3):
        draw_truck(ax, color_number=age_group, x=initial_x + (index*x_shift), y=initial_y + (index*y_shift), scale=0.5, rotation_angle = angle)

    
# first 15

for i, person in df.iterrows():
    age = person["나이"]
    alc = person["알콜농도"]
    group = person["Age Group"]

    # intersection
    # vertical, top, upwards
    if i < 15:
        draw_vehicle(101, 0, 165, 9, group, alc, i, 0)
    elif i < 30:
        new_i = i-15
        draw_vehicle(106, 0, 165, 9, group, alc, new_i, 0)
    elif i < 45:
        new_i = i-30
        draw_vehicle(111, 0, 165, 9, group, alc, new_i, 0)
    elif i < 60:
        new_i = i-45
        draw_vehicle(116.5, 0, 165, 9, group, alc, new_i, 0)
    elif i < 75:
        new_i = i-60
        draw_vehicle(121.5, 0, 165, 9, group, alc, new_i, 0)

    # vertical, bottom, upwards
    elif i < 90:
        new_i = i-75
        draw_vehicle(101, 0, 3, 9, group, alc, new_i, 0)
    elif i < 105:
        new_i = i-90
        draw_vehicle(106, 0, 3, 9, group, alc, new_i, 0)
    elif i < 120:
        new_i = i-105
        draw_vehicle(111, 0, 3, 9, group, alc, new_i, 0)
    elif i < 135:
        new_i = i-120
        draw_vehicle(116.5, 0, 3, 9, group, alc, new_i, 0)
    elif i < 150:
        new_i = i-135
        draw_vehicle(121.5, 0, 3, 9, group, alc, new_i, 0) 

    # vertical, bottom, downwards
    elif i < 165:
        new_i = i-150
        draw_vehicle(75.5, 0, 2, 9, group, alc, new_i, 180)
    elif i < 180:
        new_i = i-165
        draw_vehicle(80.5, 0, 2, 9, group, alc, new_i, 180)
    elif i < 195:
        new_i = i-180
        draw_vehicle(85.5, 0, 2, 9, group, alc, new_i, 180)
    elif i < 210:
        new_i = i-195
        draw_vehicle(91, 0, 2, 9, group, alc, new_i, 180)
    elif i < 225:
        new_i = i-210
        draw_vehicle(96, 0, 2, 9, group, alc, new_i, 180)

    # vertical, top, downwards
    elif i < 240:
        new_i = i-225
        draw_vehicle(75.5, 0, 165, 9, group, alc, new_i, 180)
    elif i < 255:
        new_i = i-240
        draw_vehicle(80.5, 0, 165, 9, group, alc, new_i, 180)
    elif i < 270:
        new_i = i-255
        draw_vehicle(85.5, 0, 165, 9, group, alc, new_i, 180)
    elif i < 285:
        new_i = i-270
        draw_vehicle(91, 0, 165, 9, group, alc, new_i, 180)
    elif i < 300:
        new_i = i-285
        draw_vehicle(96, 0, 165, 9, group, alc, new_i, 180)
    
    # horizontal, top, moving left
    elif i < 308:
        new_i = i-300
        draw_vehicle(125.5, 9, 161, 0, group, alc, new_i, 90)
    elif i < 315:
        new_i = i-308
        draw_vehicle(125.5, 9.5, 156, 0, group, alc, new_i, 90)
    elif i < 323:
        new_i = i-315
        draw_vehicle(125.5, 9, 151, 0, group, alc, new_i, 90)

    # horizontal, bottom, moving right
    elif i < 330:
        new_i = i-323
        draw_vehicle(125.5, 9, 146, 0, group, alc, new_i, 270)
    elif i < 337:
        new_i = i-330
        draw_vehicle(125.5, 9.5, 141, 0, group, alc, new_i, 270)
    elif i <= 345:
        new_i = i-337
        draw_vehicle(125.5, 9, 136, 0, group, alc, new_i, 270)

# 저장
plt.savefig("./static/intersection.png", dpi=300, bbox_inches='tight', transparent=True)

plt.show()