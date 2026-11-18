from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RegisterForm, ToolForm
from .models import BorrowRequest, Tool

def tool_list(request):
    tools = Tool.objects.select_related('owner').order_by('name')
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    if q:
        tools = tools.filter(name__icontains=q)
    if category:
        tools = tools.filter(category=category)
    return render(request, 'tools/tool_list.html', {
        'tools': tools,
        'categories': Tool.CATEGORY_CHOICES,
        'q': q,
        'selected_category': category,
    })

def tool_detail(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    can_request = False
    already_requested = False
    if request.user.is_authenticated and tool.owner != request.user:
        already_requested = tool.requests.filter(
            borrower=request.user, status='pending'
        ).exists()
        can_request = tool.status == 'available' and not already_requested
    return render(request, 'tools/tool_detail.html', {
        'tool': tool,
        'can_request': can_request,
        'already_requested': already_requested,
    })

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tool_list')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def add_tool(request):
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES)
        if form.is_valid():
            tool = form.save(commit=False)
            tool.owner = request.user
            tool.save()
            messages.success(request, 'Your tool is now listed.')
            return redirect('tool_detail', pk=tool.pk)
    else:
        form = ToolForm()
    return render(request, 'tools/tool_form.html', {'form': form})

@login_required
@require_POST
def request_tool(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    if tool.owner == request.user:
        messages.error(request, "That's your own tool.")
    elif tool.status != 'available':
        messages.error(request, 'That tool is currently borrowed.')
    elif tool.requests.filter(borrower=request.user, status='pending').exists():
        messages.info(request, 'You already have a pending request for this tool.')
    else:
        BorrowRequest.objects.create(tool=tool, borrower=request.user)
        messages.success(request, 'Request sent. The owner can now approve or decline it.')
        return redirect('my_requests')
    return redirect('tool_detail', pk=tool.pk)


@login_required
def my_requests(request):
    borrow_requests = (
        BorrowRequest.objects.filter(borrower=request.user)
        .select_related('tool')
        .order_by('-requested_at')
    )
    return render(request, 'tools/my_requests.html', {'borrow_requests': borrow_requests})

@login_required
def my_tools(request):
    tools = Tool.objects.filter(owner=request.user).order_by('name')
    incoming = (
        BorrowRequest.objects.filter(tool__owner=request.user)
        .select_related('tool', 'borrower')
        .order_by('-requested_at')
    )
    return render(request, 'tools/my_tools.html', {'tools': tools, 'incoming': incoming})


@login_required
@require_POST
def decide_request(request, pk, decision):
    # Looking the request up through tool__owner means anyone who is not the
    # owner of the tool gets a 404 - they cannot even tell the request exists.
    borrow_request = get_object_or_404(BorrowRequest, pk=pk, tool__owner=request.user)
    if borrow_request.status != 'pending':
        messages.info(request, 'That request has already been handled.')
    elif decision == 'approve':
        if borrow_request.tool.status != 'available':
            messages.error(request, 'That tool is already out on loan.')
        else:
            with transaction.atomic():
                borrow_request.status = 'approved'
                borrow_request.save()
                borrow_request.tool.status = 'borrowed'
                borrow_request.tool.save()
            messages.success(request, 'Request approved.')
            if borrow_request.borrower.email:
                send_mail(
                    subject=f'Your request for {borrow_request.tool.name} was approved',
                    message=(
                        f'Hi {borrow_request.borrower.username},\n\n'
                        f'{request.user.username} approved your request to borrow '
                        f'"{borrow_request.tool.name}".\n'
                        f'Contact them at {request.user.email} to arrange pick-up.'
                    ),
                    from_email=None,  # None = use DEFAULT_FROM_EMAIL from settings
                    recipient_list=[borrow_request.borrower.email],
                )
    else:
        borrow_request.status = 'declined'
        borrow_request.save()
        messages.success(request, 'Request declined.')
    return redirect('my_tools')


@login_required
@require_POST
def mark_returned(request, pk):
    tool = get_object_or_404(Tool, pk=pk, owner=request.user)
    tool.status = 'available'
    tool.save()
    messages.success(request, f'{tool.name} is available again.')
    return redirect('my_tools')