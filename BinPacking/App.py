import streamlit as st
import pandas as pd
from py3dbp import Packer, Bin, Item
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
from concurrent.futures import ProcessPoolExecutor

# Custom CSS to enhance the look
def add_custom_css():
    st.markdown(
        """
        <style>
        body {
            background-color: #f4f4f9;
            color: #333;
            font-family: 'Arial', sans-serif;
        }
        .main {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
            margin: 20px;
        }
        .report-container {
            margin-top: 40px;
            margin-bottom: 40px;
        }
        h1, h2, h3 {
            color: #003366;
        }
        h1 {
            font-size: 36px;
            text-align: center;
            margin-bottom: 40px;
        }
        h2 {
            font-size: 22px;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .container-info {
            font-size: 16px;
            font-weight: normal;
            color: #333;
            margin-bottom: 5px;
        }
        .container-dimensions {
            font-size: 14px;
            color: #555;
        }
        .plot-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            margin-bottom: 40px;
            background-color: #fff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border: 1px solid #ddd;
        }
        .plot-container h2, .plot-container .container-info, .plot-container .container-dimensions {
            margin: 0;
            padding: 0;
        }
        .plot {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            margin-top: 10px;
        }
        .plot img {
            display: block;
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .best-fit {
            font-weight: bold;
            color: #cc3300;
            margin-top: 20px;
            font-size: 20px;
            text-align: center;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #6c757d;
            font-size: 14px;
        }
        .bold-text {
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

add_custom_css()

# Load the Excel file
file_path = 'Optimization Problem.xlsx'
packages_df = pd.read_excel(file_path, sheet_name='Packages')
cartons_df = pd.read_excel(file_path, sheet_name='Cartons')

# Function to generate a random color
def get_random_color():
    return np.random.rand(3,)

# Function to add a 3D box (representing an item) without labels
def add_box(ax, item, color):
    pos = np.array(item.position, dtype=float)
    dim = np.array(item.get_dimension(), dtype=float)

    xx, yy = np.meshgrid([pos[0], pos[0] + dim[0]], [pos[1], pos[1] + dim[1]])
    ax.plot_surface(xx, yy, np.full_like(xx, pos[2]), color=color, alpha=0.6, edgecolor='k', linewidth=0.3)
    ax.plot_surface(xx, yy, np.full_like(xx, pos[2] + dim[2]), color=color, alpha=0.6, edgecolor='k', linewidth=0.3)

    yy, zz = np.meshgrid([pos[1], pos[1] + dim[1]], [pos[2], pos[2] + dim[2]])
    ax.plot_surface(np.full_like(yy, pos[0]), yy, zz, color=color, alpha=0.6, edgecolor='k', linewidth=0.3)
    ax.plot_surface(np.full_like(yy, pos[0] + dim[0]), yy, zz, color=color, alpha=0.6, edgecolor='k', linewidth=0.3)

    xx, zz = np.meshgrid([pos[0], pos[0] + dim[0]], [pos[2], pos[2] + dim[2]])
    ax.plot_surface(xx, np.full_like(xx, pos[1]), zz, color=color, alpha=0.6, edgecolor='k', linewidth=0.3)
    ax.plot_surface(xx, np.full_like(xx, pos[1] + dim[1]), zz, color=color, alpha=0.6, edgecolor='k', linewidth=0.3)

def save_as_pdf(cartons_df, item_data, best_fit_container, best_fit_volume_utilized_percentage, plot_images, package_id, package_dimensions):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        c = canvas.Canvas(tmpfile.name, pagesize=letter)
        width, height = letter
        margin = 40
        col_width = (width - 2 * margin) / 3
        row_height = (height - 2 * margin - 60) / 2  # Adjusted for title and footer
        y = height - margin

        def draw_page_border():
            c.setStrokeColor(colors.HexColor("#003366"))
            c.setLineWidth(1)
            c.rect(margin / 2, margin / 2, width - margin, height - margin)

        styles = getSampleStyleSheet()
        draw_page_border()

        # Center the title with package ID and dimensions
        title = f"Packing Optimization Report - {package_id} ({package_dimensions})"
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#003366"))
        title_width = c.stringWidth(title, "Helvetica-Bold", 16)
        c.drawString((width - title_width) / 2, y, title)
        y -= 20

        # Add the best fit utilization at the top in red color and center it
        if best_fit_container is not None:
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.red)
            best_fit_text = f"The best fit is {best_fit_container['Description']} ({best_fit_container['ID Length (in)']} x {best_fit_container['ID Width (in)']} x {best_fit_container['ID Height (in)']}) with a volume utilization of {best_fit_volume_utilized_percentage:.2f}%"
            best_fit_width = c.stringWidth(best_fit_text, "Helvetica-Bold", 12)
            c.drawString((width - best_fit_width) / 2, y, best_fit_text)
            y -= 20
        else:
            no_fit_text = "No suitable container found."
            no_fit_width = c.stringWidth(no_fit_text, "Helvetica-Bold", 12)
            c.setFillColor(colors.red)
            c.drawString((width - no_fit_width) / 2, y, no_fit_text)
            y -= 20

        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)

        y -= 10  # Adjust starting position for charts

        current_y = y

        for index, carton in cartons_df.iterrows():
            # Correct calculation of the number of items and volume utilized
            packer = Packer()
            storage_unit = Bin(carton['Description'], carton['ID Length (in)'], carton['ID Width (in)'], carton['ID Height (in)'], 1)
            packer.add_bin(storage_unit)
            batch_items = [Item(item_data["name"], item_data["length"], item_data["width"], item_data["height"], item_data["weight"]) for _ in range(100)]
            for item in batch_items:
                packer.add_item(item)
            packer.pack()

            total_items_fit = sum(len(b.items) for b in packer.bins)
            storage_volume = float(carton['ID Length (in)'] * carton['ID Width (in)'] * carton['ID Height (in)'])
            item_volume = float(item_data['length'] * item_data['width'] * item_data['height'])
            total_volume_utilized = float(total_items_fit * item_volume)
            volume_utilized_percentage = (total_volume_utilized / storage_volume) * 100

            col = index % 3
            row = index // 3
            img_x = margin + col * col_width
            img_y = current_y - (row * row_height)

            img_height = row_height / 2  # Adjusted height for the image
            text_y_start = img_y - img_height - 8

            # Add the image if available
            if index < len(plot_images):
                img = ImageReader(plot_images[index])
                c.drawImage(img, img_x, img_y - img_height, col_width - 10, img_height, preserveAspectRatio=True, mask='auto')

            text_y = text_y_start

            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.HexColor("#003366"))
            c.drawString(img_x, text_y, f"{carton['Description']}")
            text_y -= 10
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor("#555555"))
            c.drawString(img_x, text_y, f"({carton['ID Length (in)']} x {carton['ID Width (in)']} x {carton['ID Height (in)']})")
            text_y -= 10
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.black)
            c.drawString(img_x, text_y, "Total number of items fit: ")
            c.setFont("Helvetica-Bold", 8)
            c.drawString(img_x + 130, text_y, f"{total_items_fit}")
            text_y -= 10
            c.setFont("Helvetica", 8)
            c.drawString(img_x, text_y, "Percentage of volume utilized: ")
            c.setFont("Helvetica-Bold", 8)
            c.drawString(img_x + 130, text_y, f"{volume_utilized_percentage:.2f}%")
            text_y -= 10

            # Move to the next row if necessary
            if col == 2 and row % 2 == 1:
                current_y -= row_height
                if current_y < margin + row_height:
                    c.showPage()
                    draw_page_border()
                    current_y = height - margin - 40

        c.save()
        return tmpfile.name

def pack_items(carton, item_data, batch_size=200, num_batches=6):
    storage_unit = Bin(carton['Description'], carton['ID Length (in)'], carton['ID Width (in)'], carton['ID Height (in)'], 1)
    packer = Packer()
    packer.add_bin(storage_unit)

    for i in range(num_batches):
        batch_items = [Item(item_data["name"], item_data["length"], item_data["width"], item_data["height"], item_data["weight"]) for _ in range(batch_size)]
        for item in batch_items:
            packer.add_item(item)

    packer.pack()
    storage_volume = float(storage_unit.width * storage_unit.height * storage_unit.depth)
    item_volume = float(item_data["length"] * item_data["width"] * item_data["height"])
    total_items_fit = sum(len(b.items) for b in packer.bins)
    total_volume_utilized = float(total_items_fit * item_volume)
    volume_utilized_percentage = (total_volume_utilized / storage_volume) * 100

    return carton, total_items_fit, volume_utilized_percentage, storage_unit, packer

def generate_plot(carton, item_data, storage_unit, packer, plot_column, plot_index, plot_images):
    # Generate 3D plot
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    for b in packer.bins:
        for item in b.items:
            color = get_random_color()
            add_box(ax, item, color)
    ax.set_xlim([0, carton['ID Length (in)']])
    ax.set_ylim([0, carton['ID Width (in)']])
    ax.set_zlim([0, carton['ID Height (in)']])
    ax.set_box_aspect([carton['ID Length (in)'], carton['ID Width (in)'], carton['ID Height (in)']])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    plt.tight_layout(pad=2.0)
    plot_column.pyplot(fig)  # Display the plot in one of the three columns

    # Save plot as image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as plotfile:
        fig.savefig(plotfile.name, format='png')
        plot_images.append(plotfile.name)

    plot_column.markdown(f"""
    <div class='plot-container'>
        <h2>{carton['Description']}</h2>
        <div class='container-dimensions'>({round(carton['ID Length (in)'], 2)} x {round(carton['ID Width (in)'], 2)} x {round(carton['ID Height (in)'], 2)})</div>
        <div class='container-info'>Total number of items fit: <span class='bold-text'>{total_items_fit}</span></div>
        <div class='container-info'>Percentage of volume utilized: <span class='bold-text'>{volume_utilized_percentage:.2f}%</span></div>
    </div>
    """, unsafe_allow_html=True)

# Streamlit app layout
st.title("Packing Optimization Report")

use_custom_dimensions = st.radio("Do you want to use custom package dimensions?", ('No', 'Yes'))

if use_custom_dimensions == "Yes":
    length = round(st.number_input("Enter the package length (in inches):", min_value=0.0), 2)
    width = round(st.number_input("Enter the package width (in inches):", min_value=0.0), 2)
    height = round(st.number_input("Enter the package height (in inches):", min_value=0.0), 2)
    package_id = "CustomPackage"
    package_dimensions = f"{length} x {width} x {height}"
else:
    package_id = st.selectbox("Select the Package ID to pack:", packages_df['Package_ID'].unique())
    selected_package = packages_df[packages_df['Package_ID'] == package_id].iloc[0]
    length = round(selected_package['PKG_LNGTH_IN'], 2)
    width = round(selected_package['PKG_WIDTH_IN'], 2)
    height = round(selected_package['PKG_DEPTH_IN'], 2)
    package_dimensions = f"{length} x {width} x {height}"

if st.button("Optimize Packing"):
    item_data = {"name": package_id, "length": length, "width": width, "height": height, "weight": 0}

    best_fit_container = None
    best_fit_volume_utilized_percentage = 0

    plot_index = 0
    plot_columns = []
    plot_images = []

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(pack_items, carton, item_data) for index, carton in cartons_df.iterrows()]
        results = [future.result() for future in futures]

    for result in results:
        carton, total_items_fit, volume_utilized_percentage, storage_unit, packer = result

        if plot_index % 3 == 0:
            plot_columns = st.columns(3)  # Create a new row of three columns

        if volume_utilized_percentage > best_fit_volume_utilized_percentage:
            best_fit_container = carton
            best_fit_volume_utilized_percentage = volume_utilized_percentage

        generate_plot(carton, item_data, storage_unit, packer, plot_columns[plot_index % 3], plot_index, plot_images)
        plot_index += 1

    if best_fit_container is not None:
        st.markdown(f"""
        <div class='report-container'>
            <div class='best-fit'>The best fit is {best_fit_container["Description"]} ({round(best_fit_container['ID Length (in)'], 2)} x {round(best_fit_container['ID Width (in)'], 2)} x {round(best_fit_container['ID Height (in)'], 2)}) with a volume utilization of <span class='bold-text'>{best_fit_volume_utilized_percentage:.2f}%</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='report-container'>
            <div class='best-fit'>No suitable container found.</div>
        </div>
        """, unsafe_allow_html=True)

    # Add button to save the report as a PDF
    pdf_file = save_as_pdf(cartons_df, item_data, best_fit_container, best_fit_volume_utilized_percentage, plot_images, package_id, package_dimensions)
    with open(pdf_file, "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="Packing_Optimization_Report.pdf",
            mime="application/pdf",
        )

st.markdown("<div class='footer'>&copy; 2024 Packing Optimization Report</div>", unsafe_allow_html=True)




