"""
PDF Report Generator using ReportLab
Generates professional PDF reports for all 8 report types
"""
from typing import Dict, Any, List
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.pdfgen import canvas
import io


class PDFReportGenerator:
    """PDF Report Generator for all report types"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
        self.colors = {
            "primary": colors.HexColor("#1E40AF"),  # Blue
            "secondary": colors.HexColor("#10B981"),  # Green
            "accent": colors.HexColor("#F59E0B"),  # Orange
            "danger": colors.HexColor("#EF4444"),  # Red
            "light_blue": colors.HexColor("#DBEAFE"),
            "light_green": colors.HexColor("#D1FAE5"),
            "light_red": colors.HexColor("#FEE2E2")
        }

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        styles = {}

        # Title style
        styles['ReportTitle'] = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor("#1E40AF"),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Section Header
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        # Metadata style
        styles['Metadata'] = ParagraphStyle(
            'Metadata',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#6B7280"),
            spaceAfter=6
        )
        
        # Normal style (fallback for plain text)
        styles['Normal'] = ParagraphStyle(
            'Normal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )

        return styles

    def _create_header_footer(self, canvas_obj, doc):
        """Add header and footer to each page"""
        canvas_obj.saveState()

        # Header
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(colors.HexColor("#1E40AF"))
        canvas_obj.drawString(inch, doc.height + 1.5 * inch, "S&OP Portal Report")

        # Footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawRightString(
            doc.width + inch,
            0.5 * inch,
            f"Page {doc.page}"
        )
        canvas_obj.drawString(
            inch,
            0.5 * inch,
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        canvas_obj.restoreState()

    def _create_table(self, data: List[List[Any]], col_widths: List[float] = None, has_header: bool = True):
        """Create a styled table"""
        if not data:
            return None

        table = Table(data, colWidths=col_widths)

        # Base table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), self.colors["primary"]) if has_header else None,
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke) if has_header else None,
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold') if has_header else None,
            ('FONTSIZE', (0, 0), (-1, 0), 12) if has_header else None,
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12) if has_header else None,
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]

        # Filter out None values
        table_style = [s for s in table_style if s is not None]
        table.setStyle(TableStyle(table_style))

        return table

    def _create_bar_chart(self, data: Dict[str, float], title: str, width: int = 400, height: int = 200):
        """Create a vertical bar chart"""
        drawing = Drawing(width, height)

        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = height - 100
        chart.width = width - 100

        # Prepare data
        categories = list(data.keys())[:10]  # Top 10
        values = [data[k] for k in categories]

        chart.data = [values]
        chart.categoryAxis.categoryNames = categories
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 8
        chart.valueAxis.valueMin = 0

        chart.bars[0].fillColor = self.colors["primary"]

        drawing.add(chart)
        return drawing

    # ==========================================
    # REPORT 1: SALES SUMMARY PDF
    # ==========================================
    def generate_sales_summary_pdf(self, data: Dict[str, Any], file_path: str):
        """Generate Sales Summary PDF Report"""
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []

        # Title
        title = Paragraph(f"Sales Summary Report", self.custom_styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Metadata
        metadata = f"""
        <b>Generated:</b> {data['generatedAt']}<br/>
        <b>Report Type:</b> {data['reportType']}
        """
        story.append(Paragraph(metadata, self.custom_styles['Metadata']))
        story.append(Spacer(1, 0.3 * inch))

        # Summary Section
        summary_header = Paragraph("Overall Summary", self.custom_styles['SectionHeader'])
        story.append(summary_header)

        summary_data = data.get('summary', {})
        summary_table_data = [
            ['Metric', 'Value'],
            ['Total Revenue', f"${summary_data.get('totalRevenue', 0):,.2f}"],
            ['Total Quantity', f"{summary_data.get('totalQuantity', 0):,.2f}"],
            ['Transaction Count', f"{summary_data.get('transactionCount', 0):,}"],
            ['Average Quantity', f"{summary_data.get('avgQuantity', 0):,.2f}"]
        ]

        summary_table = self._create_table(summary_table_data, col_widths=[3 * inch, 3 * inch])
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Monthly Trends
        story.append(Paragraph("Monthly Sales Trends", self.custom_styles['SectionHeader']))

        if data.get('monthlyTrends') and len(data['monthlyTrends']) > 0:
            monthly_headers = ['Month', 'Revenue', 'Quantity', 'Transactions']
            monthly_rows = [[m['monthLabel'], f"${m['revenue']:,.2f}", f"{m['quantity']:,.0f}", m['transactions']]
                            for m in data['monthlyTrends'][:12]]  # Last 12 months

            monthly_table_data = [monthly_headers] + monthly_rows
            monthly_table = self._create_table(monthly_table_data, col_widths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
            story.append(monthly_table)
        else:
            story.append(Paragraph("No monthly trends data available", self.custom_styles['Normal']))
        
        story.append(PageBreak())

        # Top Customers
        story.append(Paragraph("Top 10 Customers", self.custom_styles['SectionHeader']))

        if data.get('topCustomers') and len(data['topCustomers']) > 0:
            customer_headers = ['Customer', 'Revenue', 'Quantity']
            customer_rows = [[c['customerName'][:30], f"${c['totalRevenue']:,.2f}", f"{c['totalQuantity']:,.0f}"]
                            for c in data['topCustomers'][:10]]

            customer_table_data = [customer_headers] + customer_rows
            customer_table = self._create_table(customer_table_data, col_widths=[3 * inch, 1.5 * inch, 1.5 * inch])
            story.append(customer_table)
        else:
            story.append(Paragraph("No customer data available", self.custom_styles['Normal']))
        
        story.append(Spacer(1, 0.3 * inch))

        # Top Products
        story.append(Paragraph("Top 10 Products", self.custom_styles['SectionHeader']))

        if data.get('topProducts') and len(data['topProducts']) > 0:
            product_headers = ['Product', 'Quantity', 'Revenue']
            product_rows = [[p['productDescription'][:30], f"{p['totalQuantity']:,.0f}", f"${p['totalRevenue']:,.2f}"]
                           for p in data['topProducts'][:10]]

            product_table_data = [product_headers] + product_rows
            product_table = self._create_table(product_table_data, col_widths=[3 * inch, 1.5 * inch, 1.5 * inch])
            story.append(product_table)
        else:
            story.append(Paragraph("No product data available", self.custom_styles['Normal']))

        # Build PDF
        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

    # ==========================================
    # REPORT 2: FORECAST VS ACTUAL PDF
    # ==========================================
    def generate_forecast_vs_actual_pdf(self, data: Dict[str, Any], file_path: str):
        """Generate Forecast vs Actual PDF Report"""
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []

        # Title
        title = Paragraph("Forecast vs Actual Comparison", self.custom_styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Summary
        summary_data = data['summary']
        summary_table_data = [
            ['Metric', 'Value'],
            ['Total Variance', f"{summary_data['totalVariance']:,.2f}"],
            ['Variance Percentage', f"{summary_data['variancePercentage']:.2f}%"],
            ['Accurate Forecasts', f"{summary_data['accurateForecasts']:,}"],
            ['Total Comparisons', f"{summary_data['totalComparisons']:,}"]
        ]

        summary_table = self._create_table(summary_table_data, col_widths=[3 * inch, 3 * inch])
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Variance Details
        story.append(Paragraph("Variance Details", self.custom_styles['SectionHeader']))

        headers = ['Customer', 'Product', 'Forecast', 'Actual', 'Variance', 'Variance %', 'Status']
        rows = []

        for item in data['varianceDetails'][:20]:  # Top 20
            status = item['status']
            rows.append([
                item['customerName'][:20],
                item['productDescription'][:20],
                f"{item['forecastQty']:,.0f}",
                f"{item['actualQty']:,.0f}",
                f"{item['variance']:,.0f}",
                f"{item['variancePercentage']:.1f}%",
                status
            ])

        variance_table_data = [headers] + rows
        variance_table = self._create_table(variance_table_data,
                                            col_widths=[1*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch, 1*inch])

        # Add color coding
        table_style = variance_table._cellStyles
        for idx, item in enumerate(data['varianceDetails'][:20], start=1):
            status = item['status']
            if status == 'Accurate':
                bg_color = self.colors["light_green"]
            elif status == 'Over Forecast':
                bg_color = self.colors["light_blue"]
            else:
                bg_color = self.colors["light_red"]

            variance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, idx), (-1, idx), bg_color)
            ]))

        story.append(variance_table)

        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

    # ==========================================
    # REPORT 3: MONTHLY DASHBOARD PDF
    # ==========================================
    def generate_monthly_dashboard_pdf(self, data: Dict[str, Any], file_path: str):
        """Generate Monthly Dashboard PDF Report"""
        doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))
        story = []

        # Title
        title = Paragraph("Monthly Dashboard", self.custom_styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Current Month KPIs
        story.append(Paragraph("Current Month KPIs", self.custom_styles['SectionHeader']))

        current_month = data['currentMonth']
        kpi_data = [
            ['Metric', 'Value'],
            ['Revenue', f"${current_month['revenue']:,.2f}"],
            ['Quantity', f"{current_month['quantity']:,.0f}"],
            ['Transactions', f"{current_month['transactions']:,}"],
            ['Avg Transaction', f"${current_month['avgTransaction']:,.2f}"]
        ]

        kpi_table = self._create_table(kpi_data, col_widths=[3 * inch, 3 * inch])
        story.append(kpi_table)
        story.append(Spacer(1, 0.3 * inch))

        # YTD Performance
        story.append(Paragraph("Year-to-Date Performance", self.custom_styles['SectionHeader']))

        ytd = data['yearToDate']
        ytd_data = [
            ['Metric', 'Value'],
            ['YTD Revenue', f"${ytd['revenue']:,.2f}"],
            ['YTD Quantity', f"{ytd['quantity']:,.0f}"],
            ['YTD Transactions', f"{ytd['transactions']:,}"]
        ]

        ytd_table = self._create_table(ytd_data, col_widths=[3 * inch, 3 * inch])
        story.append(ytd_table)
        story.append(Spacer(1, 0.3 * inch))

        # Top Customers and Products side by side
        story.append(Paragraph("Top Performers", self.custom_styles['SectionHeader']))

        # Top 5 Customers
        customer_data = [['Top Customers', 'Revenue']]
        for c in data['topCustomers'][:5]:
            customer_data.append([c['customerName'][:25], f"${c['revenue']:,.2f}"])

        # Top 5 Products
        product_data = [['Top Products', 'Quantity']]
        for p in data['topProducts'][:5]:
            product_data.append([p['productDescription'][:25], f"{p['quantity']:,.0f}"])

        # Create tables
        customer_table = self._create_table(customer_data, col_widths=[2.5 * inch, 1.5 * inch])
        product_table = self._create_table(product_data, col_widths=[2.5 * inch, 1.5 * inch])

        # Combine in a table for side-by-side layout
        combined_table = Table([[customer_table, product_table]], colWidths=[4.5 * inch, 4.5 * inch])
        combined_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        story.append(combined_table)

        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

    # ==========================================
    # ADDITIONAL REPORT GENERATORS (4-8)
    # ==========================================
    def generate_customer_performance_pdf(self, data: Dict[str, Any], file_path: str):
        """Generate Customer Performance PDF Report"""
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []

        title = Paragraph("Customer Performance Analysis", self.custom_styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Summary
        summary_data = data['summary']
        summary_table_data = [
            ['Metric', 'Value'],
            ['Total Customers', f"{summary_data['totalCustomers']:,}"],
            ['Total Revenue', f"${summary_data['totalRevenue']:,.2f}"],
            ['Avg Revenue/Customer', f"${summary_data['avgRevenuePerCustomer']:,.2f}"]
        ]

        summary_table = self._create_table(summary_table_data, col_widths=[3 * inch, 3 * inch])
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Customer Details
        story.append(Paragraph("Top 20 Customers", self.custom_styles['SectionHeader']))

        headers = ['Customer', 'Region', 'Revenue', 'Transactions', 'Products', 'Revenue %']
        rows = []

        for c in data['customers'][:20]:
            rows.append([
                c['customerName'][:20],
                c['region'][:15],
                f"${c['totalRevenue']:,.2f}",
                c['transactions'],
                c['productDiversity'],
                f"{c['revenueContribution']:.1f}%"
            ])

        customer_table_data = [headers] + rows
        customer_table = self._create_table(customer_table_data,
                                            col_widths=[1.5*inch, 1*inch, 1.2*inch, 0.9*inch, 0.8*inch, 0.9*inch])
        story.append(customer_table)

        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

    def generate_product_analysis_pdf(self, data: Dict[str, Any], file_path: str):
        """Generate Product Analysis PDF Report"""
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []

        title = Paragraph("Product Analysis Report", self.custom_styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Summary
        summary_data = data['summary']
        summary_table_data = [
            ['Metric', 'Value'],
            ['Total Products', f"{summary_data['totalProducts']:,}"],
            ['Total Revenue', f"${summary_data['totalRevenue']:,.2f}"],
            ['Total Categories', f"{summary_data['totalCategories']:,}"]
        ]

        summary_table = self._create_table(summary_table_data, col_widths=[3 * inch, 3 * inch])
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Product Details
        story.append(Paragraph("Top 20 Products", self.custom_styles['SectionHeader']))

        headers = ['Product', 'Category', 'Quantity', 'Revenue', 'Avg Price', 'Customers']
        rows = []

        for p in data['products'][:20]:
            rows.append([
                p['itemDescription'][:25],
                p['category'][:15],
                f"{p['totalQuantity']:,.0f}",
                f"${p['totalRevenue']:,.2f}",
                f"${p['avgPrice']:.2f}",
                p['customerReach']
            ])

        product_table_data = [headers] + rows
        product_table = self._create_table(product_table_data,
                                           col_widths=[1.8*inch, 1*inch, 0.9*inch, 1.2*inch, 0.8*inch, 0.8*inch])
        story.append(product_table)
        story.append(PageBreak())

        # Category Breakdown
        story.append(Paragraph("Category Breakdown", self.custom_styles['SectionHeader']))

        category_headers = ['Category', 'Revenue', 'Quantity', 'Products']
        category_rows = []

        for cat in data['categoryBreakdown'][:15]:
            category_rows.append([
                cat['category'],
                f"${cat['revenue']:,.2f}",
                f"{cat['quantity']:,.0f}",
                cat['products']
            ])

        category_table_data = [category_headers] + category_rows
        category_table = self._create_table(category_table_data,
                                            col_widths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        story.append(category_table)

        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

    def generate_cycle_submission_status_pdf(self, data: Dict[str, Any], file_path: str):
        """Generate Cycle Submission Status PDF Report"""
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []

        title = Paragraph(f"Cycle Submission Status - {data['cycle']['cycleName']}", self.custom_styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Cycle Info
        cycle_data = data['cycle']
        cycle_info = [
            ['Field', 'Value'],
            ['Cycle ID', cycle_data['cycleId']],
            ['Status', cycle_data['status']],
            ['Start Date', cycle_data['startDate']],
            ['End Date', cycle_data['endDate']]
        ]

        cycle_table = self._create_table(cycle_info, col_widths=[2.5 * inch, 3.5 * inch])
        story.append(cycle_table)
        story.append(Spacer(1, 0.3 * inch))

        # Summary
        summary_data = data['summary']
        summary_table_data = [
            ['Metric', 'Value'],
            ['Total Forecasts', f"{summary_data['totalForecasts']:,}"],
            ['Submitted', f"{summary_data['submittedForecasts']:,}"],
            ['Draft', f"{summary_data['draftForecasts']:,}"],
            ['Submission Rate', f"{summary_data['submissionRate']:.2f}%"]
        ]

        summary_table = self._create_table(summary_table_data, col_widths=[3 * inch, 3 * inch])
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Sales Rep Breakdown
        story.append(Paragraph("Sales Rep Breakdown", self.custom_styles['SectionHeader']))

        headers = ['Sales Rep', 'Total', 'Submitted', 'Draft', 'Submission %', 'Last Submission']
        rows = []

        for rep in data['salesRepBreakdown']:
            rows.append([
                rep['salesRepId'],
                rep['totalForecasts'],
                rep['submitted'],
                rep['draft'],
                f"{rep['submissionRate']:.1f}%",
                rep['lastSubmission'][:10] if rep['lastSubmission'] else 'N/A'
            ])

        rep_table_data = [headers] + rows
        rep_table = self._create_table(rep_table_data,
                                       col_widths=[1.2*inch, 0.7*inch, 0.9*inch, 0.7*inch, 1*inch, 1.2*inch])
        story.append(rep_table)

        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

    def generate_gross_profit_analysis_pdf(self, data: Dict[str, Any], file_path: str):
        """Generate Gross Profit Analysis PDF Report"""
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []

        title = Paragraph("Gross Profit Analysis", self.custom_styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Summary
        summary_data = data['summary']
        summary_table_data = [
            ['Metric', 'Value'],
            ['Total Revenue', f"${summary_data['totalRevenue']:,.2f}"],
            ['Total Cost', f"${summary_data['totalCost']:,.2f}"],
            ['Gross Profit', f"${summary_data['totalGrossProfit']:,.2f}"],
            ['Overall Margin', f"{summary_data['overallMargin']:.2f}%"]
        ]

        summary_table = self._create_table(summary_table_data, col_widths=[3 * inch, 3 * inch])
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Profit Details
        story.append(Paragraph("Top 20 Profitable Items", self.custom_styles['SectionHeader']))

        headers = ['Customer', 'Product', 'Revenue', 'Cost', 'Gross Profit', 'Margin %']
        rows = []

        for item in data['profitDetails'][:20]:
            rows.append([
                item['customerName'][:18],
                item['productDescription'][:18],
                f"${item['revenue']:,.2f}",
                f"${item['cost']:,.2f}",
                f"${item['grossProfit']:,.2f}",
                f"{item['profitMargin']:.1f}%"
            ])

        profit_table_data = [headers] + rows
        profit_table = self._create_table(profit_table_data,
                                          col_widths=[1.2*inch, 1.2*inch, 1.1*inch, 1.1*inch, 1.2*inch, 0.9*inch])
        story.append(profit_table)

        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

    def generate_forecast_accuracy_pdf(self, data: Dict[str, Any], file_path: str):
        """Generate Forecast Accuracy PDF Report"""
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []

        title = Paragraph("Forecast Accuracy Analysis", self.custom_styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Summary
        summary_data = data['summary']
        summary_table_data = [
            ['Metric', 'Value'],
            ['Total Comparisons', f"{summary_data['totalComparisons']:,}"],
            ['Overall MAPE', f"{summary_data['overallMAPE']:.2f}%"],
            ['Accuracy Rate (±10%)', f"{summary_data['accuracyRate']:.2f}%"],
            ['Accurate Forecasts', f"{summary_data['accurateForecasts']:,}"]
        ]

        summary_table = self._create_table(summary_table_data, col_widths=[3 * inch, 3 * inch])
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Sales Rep Performance
        story.append(Paragraph("Sales Rep Performance", self.custom_styles['SectionHeader']))

        headers = ['Sales Rep', 'Forecasts', 'Comparisons', 'Avg MAPE %', 'Accuracy %']
        rows = []

        for rep in data['salesRepPerformance']:
            rows.append([
                rep['salesRepId'],
                rep['totalForecasts'],
                rep['comparisons'],
                f"{rep['avgMAPE']:.2f}%",
                f"{rep['accuracyRate']:.1f}%"
            ])

        rep_table_data = [headers] + rows
        rep_table = self._create_table(rep_table_data,
                                       col_widths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        story.append(rep_table)

        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
