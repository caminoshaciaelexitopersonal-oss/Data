import React from 'react';

// Esta utilidad descarga un gráfico (renderizado por Recharts) como un archivo PNG.
// Encuentra el elemento SVG dentro del ref de React proporcionado, lo dibuja en un canvas
// con un fondo oscuro para que coincida con el tema de la aplicación, y luego activa una descarga.
export const handleDownloadChart = (chartRef: React.RefObject<HTMLDivElement>, filename: string) => {
    // 1. Encuentra el elemento SVG dentro del div contenedor del componente.
    const svg = chartRef.current?.querySelector('svg');
    if (!svg) {
        console.error("No se pudo encontrar el elemento SVG para descargar.");
        alert("Error: No se pudo encontrar el gráfico para descargar.");
        return;
    }

    // 2. Serializa el SVG a una cadena de texto y crea una URL de datos.
    const svgString = new XMLSerializer().serializeToString(svg);
    // Usamos btoa para codificar la cadena SVG para la URL de datos.
    // unescape(encodeURIComponent(...)) es un truco común para manejar caracteres UTF-8 correctamente.
    const dataUrl = `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgString)))}`;

    const img = new Image();
    
    img.onload = () => {
        // 3. Crea un canvas para dibujar la imagen.
        // Añadimos padding para asegurar que el gráfico no se recorte en los bordes.
        const padding = 20;
        const canvas = document.createElement('canvas');
        canvas.width = img.width + padding * 2;
        canvas.height = img.height + padding * 2;
        const ctx = canvas.getContext('2d');
        if (!ctx) {
             alert("Error: No se pudo crear el contexto del lienzo para generar la imagen.");
            return;
        }

        // 4. Rellena el canvas con el color de fondo oscuro de la aplicación.
        ctx.fillStyle = '#111827'; // Tailwind gray-900
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // 5. Dibuja la imagen del SVG en el canvas.
        ctx.drawImage(img, padding, padding);

        // 6. Convierte el canvas a una URL de datos PNG y activa la descarga.
        const pngUrl = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = pngUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
    
    img.onerror = () => {
        alert("Error: No se pudo cargar la imagen del gráfico para la descarga.");
    };

    img.src = dataUrl;
};


export const captureChartAsBase64 = (chartRef: React.RefObject<HTMLDivElement>): Promise<string> => {
    return new Promise((resolve, reject) => {
        const svg = chartRef.current?.querySelector('svg');
        if (!svg) {
            return reject(new Error("No se pudo encontrar el elemento SVG para capturar."));
        }

        const svgString = new XMLSerializer().serializeToString(svg);
        const dataUrl = `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgString)))}`;

        const img = new Image();
        img.onload = () => {
            const padding = 20;
            const canvas = document.createElement('canvas');
            canvas.width = img.width + padding * 2;
            canvas.height = img.height + padding * 2;
            const ctx = canvas.getContext('2d');
            if (!ctx) {
                return reject(new Error("No se pudo crear el contexto del lienzo para generar la imagen."));
            }

            ctx.fillStyle = '#111827'; // Tailwind gray-900
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, padding, padding);

            const jpegUrl = canvas.toDataURL('image/jpeg', 0.9); // Use JPEG for smaller size
            // Return only the base64 part
            resolve(jpegUrl.split(',')[1]);
        };
        img.onerror = () => {
            reject(new Error("No se pudo cargar la imagen del gráfico para la captura."));
        };
        img.src = dataUrl;
    });
};