import geopandas as gpd
import matplotlib.pyplot as plt
import argparse

def main():
    # Configuración de argumentos
    parser = argparse.ArgumentParser(
        description='Validación y generación de aptitud para predios en Tunja'
    )
    parser.add_argument('--predio', required=True, help='Ruta del shapefile del predio')
    parser.add_argument('--aptitudes', required=True, help='Ruta del shapefile de aptitudes de Tunja')
    parser.add_argument('--output_shp', required=True, help='Ruta de salida para el nuevo shapefile')
    parser.add_argument('--output_png', required=True, help='Ruta de salida para el archivo PNG')
    args = parser.parse_args()

    # Carga de los shapefiles
    gdf_aptitudes = gpd.read_file(args.aptitudes)
    gdf_predio = gpd.read_file(args.predio)

    # Asegurarse de que ambos tengan el mismo CRS
    if gdf_aptitudes.crs != gdf_predio.crs:
        gdf_predio = gdf_predio.to_crs(gdf_aptitudes.crs)

    # Validación: verificar si el predio se encuentra dentro del área de aptitudes
    # Se crea una unión de todas las geometrías de aptitudes
    aptitudes_union = gdf_aptitudes.unary_union

    # Usamos 'within' para verificar si el predio está totalmente contenido
    if not gdf_predio.geometry.iloc[0].within(aptitudes_union):
        print("El predio no se encuentra dentro del área de aptitudes de Tunja.")
        return

    # Calcular la intersección entre el predio y el área de aptitudes
    interseccion = gpd.overlay(gdf_predio, gdf_aptitudes, how='intersection')

    if interseccion.empty:
        print("No se encontró intersección entre el predio y el área de aptitudes.")
        return

    # Exportar el shapefile resultante
    interseccion.to_file(args.output_shp)
    print(f"Nuevo shapefile guardado en: {args.output_shp}")

    # Generar y guardar el mapa en PNG
    fig, ax = plt.subplots(figsize=(10, 10))
    interseccion.plot(ax=ax, cmap='viridis', alpha=0.5, label='Intersección', column='Descripcio', legend=True)
    #plt.legend()
    plt.title("Intersección entre el predio y aptitudes de Tunja")
    plt.savefig(args.output_png)
    plt.close()
    print(f"Mapa PNG guardado en: {args.output_png}")

    # Calcular el área de la intersección (asegúrate de que el CRS sea proyectado, p.ej. metros)
    interseccion['area'] = interseccion.area
    total_area = interseccion['area'].sum()

    # Mostrar en la línea de comandos la tabla de áreas
    print("Tabla de áreas de aptitud para el predio:")
    print(interseccion[['area']])
    print(f"Área total de aptitud en el predio: {total_area:.2f} (unidades del CRS)")

if __name__ == '__main__':
    main()
