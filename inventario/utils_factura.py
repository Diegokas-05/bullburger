# inventario/utils_factura.py
import os
from decimal import Decimal
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from datetime import datetime


def generar_factura_pdf(pedido):
    """
    Genera una factura PDF formal y profesional, estilo recibo contable.
    """
    # === Configurar carpeta destino ===
    carpeta_facturas = os.path.join(settings.MEDIA_ROOT, "facturas")
    os.makedirs(carpeta_facturas, exist_ok=True)
    filename = f"factura_pedido_{pedido.id}.pdf"
    path_pdf = os.path.join(carpeta_facturas, filename)

    # === Documento base ===
    doc = SimpleDocTemplate(
        path_pdf,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=80,
        bottomMargin=50
    )
    elementos = []
    styles = getSampleStyleSheet()

    # === Estilos personalizados ===
    estilo_titulo = ParagraphStyle(
        name="Titulo",
        fontName="Times-Bold",
        fontSize=14,
        leading=21,  # interlineado 1.5 (14 * 1.5)
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    estilo_texto = ParagraphStyle(
        name="Texto",
        fontName="Times-Roman",
        fontSize=12,
        leading=18,  # interlineado 1.5 (12 * 1.5)
        alignment=TA_LEFT,
    )

    estilo_tabla = ParagraphStyle(
        name="Tabla",
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
    )

    estilo_derecha = ParagraphStyle(
        name="Derecha",
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        alignment=TA_RIGHT,
    )

    # === Buscar logo ===
    logo_path = None
    possible_paths = []

    # STATIC_ROOT (producción)
    if getattr(settings, 'STATIC_ROOT', None):
        possible_paths.append(os.path.join(settings.STATIC_ROOT, "img", "logo_bullburger.png"))

    # STATICFILES_DIRS (desarrollo)
    if hasattr(settings, 'STATICFILES_DIRS'):
        for d in settings.STATICFILES_DIRS:
            possible_paths.append(os.path.join(d, "img", "logo_bullburger.png"))

    # Ruta local alternativa
    possible_paths.append(os.path.join(settings.BASE_DIR, "static", "img", "logo_bullburger.png"))

    for path in possible_paths:
        if os.path.exists(path):
            logo_path = path
            break

    # === Encabezado ===
    if logo_path:
        logo = Image(logo_path, width=1.2 * inch, height=1.2 * inch)
    else:
        logo = Paragraph("BullBurger", estilo_titulo)

    header_data = [
        [
            logo,
            Paragraph("<b>BULLBURGER</b><br/>Restaurante & Fast Food", estilo_texto),
            Paragraph(
                f"<b>Factura N°:</b> {pedido.id}<br/>"
                f"<b>Fecha:</b> {pedido.fecha.strftime('%d/%m/%Y %H:%M')}<br/>",
                estilo_texto
            )
        ]
    ]

    header_table = Table(header_data, colWidths=[90, 280, 150])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
    ]))
    elementos.append(header_table)
    elementos.append(Spacer(1, 25))

    # === Título principal ===
    elementos.append(Paragraph("FACTURA DE VENTA", estilo_titulo))
    elementos.append(Spacer(1, 10))

    # === Datos del cliente ===
    cliente_info = (
        f"<b>Cliente:</b> {pedido.usuario.nombre}<br/>"
        f"<b>Correo:</b> {pedido.usuario.email}<br/>"
        f"<b>Teléfono:</b> {pedido.usuario.telefono or 'N/A'}<br/>"
    )
    if pedido.tipo_entrega == "domicilio":
        cliente_info += f"<b>Dirección:</b> {pedido.direccion_entrega or 'N/A'}<br/>"

    elementos.append(Paragraph("<b>Datos del Cliente</b>", estilo_texto))
    elementos.append(Spacer(1, 4))
    elementos.append(Paragraph(cliente_info, estilo_texto))
    elementos.append(Spacer(1, 15))

    # === Tabla de productos ===
    detalles = pedido.detallepedido_set.all()
    data = [["Producto", "Cantidad", "Precio Unit.", "Subtotal"]]
    total = Decimal("0.00")

    for d in detalles:
        subtotal = d.subtotal
        total += subtotal
        data.append([
            d.producto.nombre,
            str(d.cantidad),
            f"${d.producto.precio:.2f}",
            f"${subtotal:.2f}"
        ])

    tabla = Table(data, colWidths=[220, 80, 100, 100])
    tabla.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Times-Roman', 12),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 20))

    # === Total final ===
    total_text = Paragraph(
        f"<b>Total a pagar: ${total:.2f}</b>",
        estilo_derecha
    )
    elementos.append(total_text)
    elementos.append(Spacer(1, 25))

    # === Información adicional ===
    pago_info = (
        f"<b>Método de Pago:</b> {pedido.metodo_pago.capitalize()}<br/>"
        f"<b>Tipo de Entrega:</b> {'Domicilio' if pedido.tipo_entrega == 'domicilio' else 'Recoger en local'}<br/>"
    )
    elementos.append(Paragraph("<b>Detalles del Pedido</b>", estilo_texto))
    elementos.append(Spacer(1, 4))
    elementos.append(Paragraph(pago_info, estilo_texto))
    elementos.append(Spacer(1, 20))

    # === Pie de página ===
    pie = Paragraph(
        "Gracias por tu compra en BullBurger<br/>"
        "Síguenos en Instagram @BullBurgerSV — Tel: 7890-1234",
        ParagraphStyle(
            name="Pie",
            fontName="Times-Italic",
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.gray
        )
    )
    elementos.append(pie)

    # === Construir PDF ===
    doc.build(elementos)
    return os.path.join(settings.MEDIA_URL, "facturas", filename)
