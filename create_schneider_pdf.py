"""
Generador de PDF Schneider Electric - Alternativa con ReportLab
Crea un PDF profesional directamente sin depender de weasyprint
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
import os

def create_schneider_pdf_reportlab():
    """Crear PDF profesional para Schneider Electric usando ReportLab"""
    
    # Configuración del documento
    filename = "NeXOptimIA_Schneider_Electric_Partnership.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, 
                          rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2E7D32'),
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#1976D2'),
        borderWidth=1,
        borderColor=colors.HexColor('#2196F3'),
        borderPadding=5
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        spaceAfter=10,
        textColor=colors.HexColor('#F57C00')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leftIndent=20,
        bulletIndent=10
    )
    
    # Contenido del PDF
    story = []
    
    # Página de título
    story.append(Paragraph("🏢 NeXOptimIA", title_style))
    story.append(Paragraph("Strategic Partnership Proposal", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph("Schneider Electric - Digital Applications Engineer", heading_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Información del documento
    info_data = [
        ['Prepared by:', 'Jorge Bravo Chaves - OPNeXOS'],
        ['Date:', 'August 2025'],
        ['Version:', '1.0.0-MVP'],
        ['Platform:', 'NeXOptimIA - Smart Cities Costa Rica']
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(info_table)
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph("🎯 EXECUTIVE SUMMARY", heading_style))
    story.append(Paragraph(
        "NeXOptimIA is a comprehensive Edge AI platform designed to optimize critical infrastructure "
        "across 5 key sectors in Costa Rica and Latin America. We present a unique partnership opportunity "
        "for Schneider Electric to access a $2.3B market through innovative technology and strategic distribution.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Business Opportunity Table
    business_data = [
        ['Market Metric', 'Value', 'Timeline'],
        ['LATAM TAM', '$2.3B Smart Grid Market', 'Current'],
        ['Costa Rica SAM', '$500M+ (5 sectors)', 'Current'],
        ['Year 1 Target', '$500K revenue', '2025'],
        ['Year 5 Projection', '$50M+ revenue', '2030'],
        ['Partnership Model', '60/40 revenue sharing', 'Immediate']
    ]
    
    business_table = Table(business_data, colWidths=[2*inch, 2.5*inch, 1.5*inch])
    business_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA'))
    ]))
    story.append(business_table)
    story.append(PageBreak())
    
    # Platform Overview
    story.append(Paragraph("🚀 PLATFORM OVERVIEW", heading_style))
    
    modules = [
        ("⚡ Electrical Grid Optimization (ICE)", [
            "AI Prediction: 72-hour demand forecasting",
            "Blackout Prevention: 85% reduction in power outages", 
            "Grid Efficiency: Real-time load balancing",
            "Cost Savings: $15M+ annually for ICE"
        ]),
        ("💧 Water Management (AyA)", [
            "Leak Detection: Instant identification and location",
            "Distribution Optimization: 25% loss reduction",
            "Predictive Maintenance: Preventive infrastructure care",
            "Water Quality: Real-time monitoring and alerts"
        ]),
        ("🌬️ Environmental Monitoring (MINAE)", [
            "Air Quality: Real-time pollution tracking",
            "Compliance: National environmental standards",
            "Alert System: Immediate contamination warnings",
            "Historical Analytics: Trend analysis and reporting"
        ]),
        ("🚗 Intelligent Transportation (MOPT)", [
            "Traffic Optimization: 30% congestion reduction",
            "Smart Traffic Lights: AI-powered signal management",
            "GAM Coverage: Greater Metropolitan Area focus",
            "Real-time Analytics: Traffic flow optimization"
        ]),
        ("🌱 Smart Agriculture (SENASA)", [
            "Crop Monitoring: Coffee, banana, pineapple focus",
            "Water Efficiency: 50% irrigation savings",
            "Yield Improvement: 20% production increase",
            "Predictive Analytics: Weather and pest management"
        ])
    ]
    
    for module_name, features in modules:
        story.append(Paragraph(module_name, subheading_style))
        for feature in features:
            story.append(Paragraph(f"• {feature}", bullet_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Technical Specifications
    story.append(Paragraph("🤖 TECHNICAL SPECIFICATIONS", heading_style))
    
    tech_specs = [
        ['Component', 'Specification', 'Performance'],
        ['Hardware Platform', 'Raspberry Pi Pico W + RFM95W', 'LoRa 915MHz'],
        ['AI Framework', 'TensorFlow Lite', '95% accuracy'],
        ['Algorithms', 'LSTM, Isolation Forest, Random Forest', '<150ms response'],
        ['Communication', 'LoRa 915MHz SUTEL compliant', '10km range'],
        ['Backend', 'FastAPI + Python 3.11+', 'Scalable'],
        ['Database', 'PostgreSQL + InfluxDB', 'Time-series optimized']
    ]
    
    tech_table = Table(tech_specs, colWidths=[2*inch, 2.5*inch, 1.5*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F1F8E9'))
    ]))
    story.append(tech_table)
    story.append(PageBreak())
    
    # Partnership Proposal
    story.append(Paragraph("💼 PARTNERSHIP PROPOSAL", heading_style))
    
    story.append(Paragraph("🎯 Strategic Value for Schneider:", subheading_style))
    schneider_values = [
        "Market Access: Immediate entry to $500M+ Costa Rica market",
        "Technology Integration: NeXOptimIA complements existing portfolio",
        "Regional Expansion: LATAM distribution through proven local partner",
        "Innovation Leadership: Edge AI technology leadership position"
    ]
    for value in schneider_values:
        story.append(Paragraph(f"• {value}", bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("🤝 Partnership Structure:", subheading_style))
    partnership_terms = [
        "Distribution Rights: LATAM exclusive partnership",
        "Revenue Sharing: 60% OPNeXOX / 40% Schneider Electric",
        "Joint Investment: $2M initial development fund",
        "Go-to-Market: Q4 2025 launch timeline",
        "Support: Technical integration and sales enablement"
    ]
    for term in partnership_terms:
        story.append(Paragraph(f"• {term}", bullet_style))
    
    story.append(PageBreak())
    
    # Financial Projections
    story.append(Paragraph("📈 FINANCIAL PROJECTIONS", heading_style))
    
    financial_data = [
        ['Year', 'Revenue Target', 'Market Coverage', 'Key Milestones'],
        ['2025', '$500K', 'Costa Rica Pilot', 'ICE partnership, 50 sensors'],
        ['2026', '$2M', 'Costa Rica Full', 'National deployment'],
        ['2027', '$8M', '3 LATAM countries', 'Regional expansion'],
        ['2028', '$20M', '8 LATAM countries', 'Market leadership'],
        ['2029', '$50M', '15 LATAM countries', 'Platform maturity']
    ]
    
    financial_table = Table(financial_data, colWidths=[0.8*inch, 1.2*inch, 1.5*inch, 2.5*inch])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF3E0'))
    ]))
    story.append(financial_table)
    story.append(PageBreak())
    
    # Next Steps
    story.append(Paragraph("🚀 NEXT STEPS", heading_style))
    
    story.append(Paragraph("Immediate Actions (30 days):", subheading_style))
    immediate_actions = [
        "Technical Demonstration: Live platform walkthrough",
        "Pilot Proposal: Costa Rica proof-of-concept",
        "Partnership Terms: Detailed agreement negotiation",
        "Market Entry Strategy: LATAM expansion planning"
    ]
    for action in immediate_actions:
        story.append(Paragraph(f"1. {action}", bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Phase 1 Milestones (6 months):", subheading_style))
    milestones = [
        "Costa Rica Deployment: 50 sensors across GAM",
        "ICE Integration: Grid optimization pilot",
        "Performance Validation: 95%+ accuracy demonstration", 
        "Business Case: Proven ROI documentation"
    ]
    for milestone in milestones:
        story.append(Paragraph(f"• {milestone}", bullet_style))
    
    story.append(PageBreak())
    
    # Contact Information
    story.append(Paragraph("📞 CONTACT INFORMATION", heading_style))
    
    contact_data = [
        ['Contact', 'Information'],
        ['Name', 'Jorge Bravo Chaves'],
        ['Position', 'Founder & CEO - OPNeXOS'],
        ['Email', 'jorge.bravo@opnexos.cr'],
        ['Phone', '+506 8XXX-XXXX'],
        ['Website', 'countercorehazardav.com'],
        ['Location', 'San José, Costa Rica 🇨🇷'],
        ['Platform Demo', 'http://localhost:8000'],
        ['Documentation', 'http://localhost:8000/docs']
    ]
    
    contact_table = Table(contact_data, colWidths=[2*inch, 4*inch])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B1FA2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3E5F5'))
    ]))
    story.append(contact_table)
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("© 2025 OPNeXOX - NeXOptimIA", 
                          ParagraphStyle('Footer', parent=styles['Normal'], 
                                       fontSize=10, alignment=TA_CENTER,
                                       textColor=colors.HexColor('#666666'))))
    story.append(Paragraph("Transforming Infrastructure Through Edge AI - Costa Rica 🇨🇷", 
                          ParagraphStyle('Footer2', parent=styles['Normal'], 
                                       fontSize=9, alignment=TA_CENTER,
                                       textColor=colors.HexColor('#888888'))))
    
    # Generar PDF
    try:
        doc.build(story)
        file_size = os.path.getsize(filename)
        
        print(f"✅ PDF generado exitosamente: {filename}")
        print(f"📄 Tamaño: {file_size / 1024:.1f} KB")
        print(f"📁 Ubicación: {os.path.abspath(filename)}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Generando PDF para Schneider Electric...")
    print("=" * 60)
    
    pdf_file = create_schneider_pdf_reportlab()
    
    if pdf_file:
        print("\n🎯 PRESENTACIÓN LISTA PARA SCHNEIDER ELECTRIC")
        print("📧 PDF listo para envío al ingeniero de aplicaciones")
        print("💼 Documento comercial profesional completo")
        print("🏢 Partnership proposal detallada incluida")
        print("=" * 60)
    else:
        print("\n❌ Error en generación de PDF")
        print("🔧 Revisar dependencias e intentar nuevamente")
