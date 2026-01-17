from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Payment 

class DashboardService:
    """
    Service to handle data aggregation for the Admin Finance Dashboard. 
    """

    @staticmethod
    def get_dashboard_data(period="30_days", vehicle_id=None, agent_id=None):
        queryset = Payment.objects.filter(payment_status='success')
        
        # --- Date Filter ---
        today = timezone.now()
        start_date = today - timedelta(days=30) # Default

        if period == 'today':
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == '3_months':
            start_date = today - timedelta(days=90)
        elif period == 'year':
            start_date = today - timedelta(days=365)
            
        queryset = queryset.filter(timestamp__gte=start_date)

        # --- Specific Filters ---
        if vehicle_id:
            queryset = queryset.filter(vehicle__id=vehicle_id)

        if agent_id:
            queryset = queryset.filter(collected_by__id=agent_id)

        # --- Aggregations ---
        total_revenue = queryset.aggregate(Sum('amount'))['amount__sum'] or 0
        total_transactions = queryset.count()
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0

        # --- Graph Data ---
        if period == 'year':
            graph_data = (
                queryset
                .annotate(date=TruncMonth('timestamp'))
                .values('date')
                .annotate(total=Sum('amount'))
                .order_by('date')
            )
        else:
            graph_data = (
                queryset
                .annotate(date=TruncDay('timestamp'))
                .values('date')
                .annotate(total=Sum('amount'))
                .order_by('date')
            )

        # --- Agent Performance ---
        agent_performance = (
            queryset.filter(payment_method='agent')
            .values('collected_by__id', 'collected_by__user__email', 'collected_by__full_name')
            .annotate(
                total_collected=Sum('amount'),
                transaction_count=Count('id')
            )
            .order_by('-total_collected')[:5]
        )

        top_agents_clean = []
        for agent in agent_performance:
            # Use full name if available, else email
            name = agent['collected_by__full_name'] or agent['collected_by__user__email'] or "Unknown Agent"
            top_agents_clean.append({
                "id": agent['collected_by__id'],
                "collected_by": name,
                "total_collected": agent['total_collected'],
                "transaction_count": agent['transaction_count']
            })

        # --- Method Breakdown ---
        method_breakdown = (
            queryset.values('payment_method')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        # --- Recent Transactions ---
        recent_transactions = queryset.select_related('vehicle', 'collected_by').order_by('-timestamp')[:10]
        recent_data = []
        for p in recent_transactions:
            if p.collected_by:
                agent_name = p.collected_by.full_name
            else:
                agent_name = "System/Online"

            recent_data.append({
                "id": p.id,
                "plate_number": p.vehicle.plate_number,
                "amount": p.amount,
                "method": p.get_payment_method_display(),
                "agent": agent_name,
                "date": p.timestamp
            })

        return {
            "summary": {
                "total_revenue": total_revenue,
                "total_transactions": total_transactions,
                "average_value": round(avg_transaction, 2)
            },
            "graph_data": list(graph_data),
            "top_agents": top_agents_clean,
            "payment_methods": list(method_breakdown),
            "recent_transactions": recent_data
        }
