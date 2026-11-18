from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import BorrowRequest, Tool

User = get_user_model()


class ToolShareTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('olivia', 'olivia@example.com', 'pass12345!')
        self.borrower = User.objects.create_user('ben', 'ben@example.com', 'pass12345!')
        self.drill = Tool.objects.create(
            owner=self.owner, name='Cordless drill', category='power',
            description='18V with two batteries',
        )
        self.ladder = Tool.objects.create(
            owner=self.owner, name='Step ladder', category='ladders',
        )

    # Story: search tools by category
    def test_browse_and_filter_by_category(self):
        response = self.client.get(reverse('tool_list'))
        self.assertContains(response, 'Cordless drill')
        self.assertContains(response, 'Step ladder')
        response = self.client.get(reverse('tool_list'), {'category': 'ladders'})
        self.assertContains(response, 'Step ladder')
        self.assertNotContains(response, 'Cordless drill')
        response = self.client.get(reverse('tool_list'), {'q': 'drill'})
        self.assertContains(response, 'Cordless drill')
        self.assertNotContains(response, 'Step ladder')

    # Story: log in securely - private pages need a login
    def test_private_pages_redirect_to_login(self):
        for name in ('add_tool', 'my_tools', 'my_requests'):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302)
            self.assertIn('/accounts/login/', response['Location'])

    # Story: list a tool
    def test_owner_can_list_a_tool(self):
        self.client.login(username='olivia', password='pass12345!')
        response = self.client.post(reverse('add_tool'), {
            'name': 'Hedge trimmer', 'category': 'garden', 'description': 'Petrol',
        })
        tool = Tool.objects.get(name='Hedge trimmer')
        self.assertRedirects(response, reverse('tool_detail', args=[tool.pk]))
        self.assertEqual(tool.owner, self.owner)
        self.assertEqual(tool.status, 'available')

    # The whole happy path from the worksheet
    def test_happy_path_request_approve_return(self):
        self.client.login(username='ben', password='pass12345!')
        self.client.post(reverse('request_tool', args=[self.drill.pk]))
        borrow_request = BorrowRequest.objects.get(tool=self.drill)
        self.assertEqual(borrow_request.borrower, self.borrower)
        self.assertEqual(borrow_request.status, 'pending')

        self.client.logout()
        self.client.login(username='olivia', password='pass12345!')
        response = self.client.get(reverse('my_tools'))
        self.assertContains(response, 'ben')
        self.client.post(reverse('approve_request', args=[borrow_request.pk]))
        borrow_request.refresh_from_db()
        self.drill.refresh_from_db()
        self.assertEqual(borrow_request.status, 'approved')
        self.assertEqual(self.drill.status, 'borrowed')

        self.client.post(reverse('mark_returned', args=[self.drill.pk]))
        self.drill.refresh_from_db()
        self.assertEqual(self.drill.status, 'available')

    def test_owner_can_decline(self):
        borrow_request = BorrowRequest.objects.create(tool=self.drill, borrower=self.borrower)
        self.client.login(username='olivia', password='pass12345!')
        self.client.post(reverse('decline_request', args=[borrow_request.pk]))
        borrow_request.refresh_from_db()
        self.drill.refresh_from_db()
        self.assertEqual(borrow_request.status, 'declined')
        self.assertEqual(self.drill.status, 'available')

    # Rules the spec implies
    def test_cannot_request_your_own_tool(self):
        self.client.login(username='olivia', password='pass12345!')
        self.client.post(reverse('request_tool', args=[self.drill.pk]))
        self.assertEqual(BorrowRequest.objects.count(), 0)

    def test_cannot_request_a_borrowed_tool(self):
        self.drill.status = 'borrowed'
        self.drill.save()
        self.client.login(username='ben', password='pass12345!')
        self.client.post(reverse('request_tool', args=[self.drill.pk]))
        self.assertEqual(BorrowRequest.objects.count(), 0)

    def test_duplicate_pending_request_is_ignored(self):
        self.client.login(username='ben', password='pass12345!')
        self.client.post(reverse('request_tool', args=[self.drill.pk]))
        self.client.post(reverse('request_tool', args=[self.drill.pk]))
        self.assertEqual(BorrowRequest.objects.count(), 1)

    # Story: owner controls who borrows - nobody else can decide
    def test_only_the_owner_can_approve(self):
        borrow_request = BorrowRequest.objects.create(tool=self.drill, borrower=self.borrower)
        self.client.login(username='ben', password='pass12345!')
        response = self.client.post(reverse('approve_request', args=[borrow_request.pk]))
        self.assertEqual(response.status_code, 404)
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, 'pending')

    def test_state_changes_need_post(self):
        borrow_request = BorrowRequest.objects.create(tool=self.drill, borrower=self.borrower)
        self.client.login(username='olivia', password='pass12345!')
        response = self.client.get(reverse('approve_request', args=[borrow_request.pk]))
        self.assertEqual(response.status_code, 405)

        # Stretch goal: the borrower is emailed when a request is approved
    def test_approval_sends_an_email_to_the_borrower(self):
        borrow_request = BorrowRequest.objects.create(tool=self.drill, borrower=self.borrower)
        self.client.login(username='olivia', password='pass12345!')
        self.client.post(reverse('approve_request', args=[borrow_request.pk]))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['ben@example.com'])
        self.assertIn('Cordless drill', mail.outbox[0].subject)