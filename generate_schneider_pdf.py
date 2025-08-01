"""
Generador de PDF - Presentación Schneider Electric
Convierte el documento markdown a PDF profesional
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path
import os

def create_schneider_pdf():
    """Generar PDF profesional para Schneider Electric"""
    
    # Leer el archivo markdown
    md_file = "SCHNEIDER_ELECTRIC_PRESENTATION.md"
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convertir markdown a HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'toc'])
    
    # CSS profesional para el PDF
    css_styles = """
    @page {
        size: A4;
        margin: 2cm;
        @top-center {
            content: "NexusOptim IA - Schneider Electric Partnership";
            font-size: 10pt;
            color: #666;
        }
        @bottom-right {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10pt;
            color: #666;
        }
    }
    
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        font-size: 11pt;
    }
    
    h1 {
        color: #2E7D32;
        font-size: 24pt;
        margin-bottom: 20px;
        border-bottom: 3px solid #4CAF50;
        padding-bottom: 10px;
    }
    
    h2 {
        color: #1976D2;
        font-size: 18pt;
        margin-top: 25px;
        margin-bottom: 15px;
        border-left: 4px solid #2196F3;
        padding-left: 15px;
    }
    
    h3 {
        color: #F57C00;
        font-size: 14pt;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    h4 {
        color: #7B1FA2;
        font-size: 12pt;
        margin-top: 15px;
        margin-bottom: 8px;
    }
    
    p {
        margin-bottom: 10px;
        text-align: justify;
    }
    
    ul, ol {
        margin-bottom: 15px;
        padding-left: 25px;
    }
    
    li {
        margin-bottom: 5px;
    }
    
    strong {
        color: #1565C0;
        font-weight: 600;
    }
    
    em {
        color: #D32F2F;
        font-style: italic;
    }
    
    code {
        background-color: #F5F5F5;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
    }
    
    pre {
        background-color: #F8F8F8;
        border: 1px solid #E0E0E0;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
        overflow-x: auto;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 15px 0;
    }
    
    th, td {
        border: 1px solid #DDD;
        padding: 8px;
        text-align: left;
    }
    
    th {
        background-color: #F0F0F0;
        font-weight: bold;
    }
    
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #4CAF50, #2196F3, #FF9800);
        margin: 30px 0;
    }
    
    .highlight {
        background-color: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 15px;
        margin: 15px 0;
    }
    
    .page-break {
        page-break-before: always;
    }
    """
    
    # HTML completo con estilos
    full_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NexusOptim IA - Schneider Electric Partnership</title>
        <style>{css_styles}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Generar PDF
    try:
        output_file = "NexusOptim_IA_Schneider_Electric_Partnership.pdf"
        HTML(string=full_html).write_pdf(output_file)
        
        print(f"✅ PDF generado exitosamente: {output_file}")
        print(f"📄 Tamaño: {os.path.getsize(output_file) / 1024:.1f} KB")
        print(f"📁 Ubicación: {os.path.abspath(output_file)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Generando PDF para Schneider Electric...")
    print("=" * 60)
    
    pdf_file = create_schneider_pdf()
    
    if pdf_file:
        print("\n🎯 PRESENTACIÓN LISTA PARA SCHNEIDER ELECTRIC")
        print("📧 PDF listo para envío al ingeniero de aplicaciones")
        print("💼 Documento comercial profesional completo")
        print("=" * 60)
    else:
        print("\n❌ Error en generación de PDF")
        print("🔧 Revisar dependencias e intentar nuevamente")
