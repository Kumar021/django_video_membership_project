from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Membership, UserMembership, Subscription, Address

import stripe

import razorpay

# User = settings.AUTH_USER_MODEL

def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None


def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(
        user_membership=get_user_membership(request))
    if user_subscription_qs.exists():
        user_subscription = user_subscription_qs.first()
        return user_subscription
    return None


def get_selected_membership(request):
    membership_type = request.session['selected_membership_type']
    selected_membership_qs = Membership.objects.filter(
        membership_type=membership_type)
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None

def get_billing_address(request):
    address_qs = Address.objects.filter(user=request.user)
    if address_qs.count() == 1:
        return address_qs.first()
    return None

@login_required
def billing_address(request):
    if request.method == "POST":
        name = request.POST["name"]
        address1 = request.POST["address1"]
        address2 = request.POST["address2"]
        city = request.POST["city"]
        state = request.POST["state"]
        zip_code = request.POST["zip_code"]
        country = request.POST["country"]

        address_obj = Address.objects.create(
                user = request.user,
                address1 = address1,
                address2 = address2,
                city = city,
                state = state,
                zip_code = zip_code,
                country = country
            )
        user_obj = User.objects.filter(username=request.user).update(first_name=name)
        messages.info(request, "Address added successfully!!!")
        return redirect("memberships:profile")

    context = {}
    return render(request, "memberships/billing_address.html", context)

@login_required
def profile_view(request):
    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)
    billing_obj = get_billing_address(request)
    # if billing_obj is None:
    #     return redirect('billing')
    context = {
        'user_membership': user_membership,
        'user_subscription': user_subscription,
        'address_obj': billing_obj
    }
    return render(request, "memberships/profile.html", context)


class MembershipSelectView(LoginRequiredMixin, ListView):
    model = Membership

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = get_user_membership(self.request)
        context['current_membership'] = str(current_membership.membership)
        return context

    def post(self, request, **kwargs):
        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)
        selected_membership_type = request.POST.get('membership_type')

        selected_membership = Membership.objects.get(
            membership_type=selected_membership_type)

        if user_membership.membership == selected_membership:
            if user_subscription is not None:
                messages.info(request, """You already have this membership. Your
                              next payment is due {}""".format('get this value from stripe'))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # assign to the session
        request.session['selected_membership_type'] = selected_membership.membership_type

        return HttpResponseRedirect(reverse('memberships:payment'))

@login_required
def PaymentView(request):
    billing_obj = get_billing_address(request)
    if billing_obj is None:
        return redirect('billing')

    user_membership = get_user_membership(request)
    try:
        selected_membership = get_selected_membership(request)
    except:
        return redirect(reverse("memberships:select"))
    publishKey = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == "POST":
        try:
            token = request.POST['stripeToken']

            # UPDATE FOR STRIPE API CHANGE 2018-05-21

            '''
            First we need to add the source for the customer
            '''

            address_qs = Address.objects.filter(user=request.user)
            address_obj = None
            if address_qs.count() == 1:
                address_obj = address_qs.first()
            if address_obj is None:
                messages.info(request, "Address is required!!")
                return redirect('memberships:profile')
            address = {
                'line1': address_obj.address1,
                'line2': address_obj.address2,
                'postal_code': address_obj.zip_code,
                'city': address_obj.city,
                'state': address_obj.state,
                'country': address_obj.country,
            }
            customer = stripe.Customer.retrieve(user_membership.stripe_customer_id)
            customer.address = address
            customer.name = request.user
            customer.source = token # 4242424242424242
            customer.save()

            # '''
            # Now we can create the subscription using only the customer as we don't need to pass their
            # credit card source anymore
            # '''

            subscription = stripe.Subscription.create(
                customer=user_membership.stripe_customer_id,
                items=[
                    # { "plan": selected_membership.stripe_plan_id },
                    {"price": selected_membership.stripe_plan_id},
                ]
            )
            return redirect(reverse('memberships:update-transactions',
                                    kwargs={
                                        'subscription_id': subscription.id
                                    }))
                

        except:
            messages.info(request, "An error has occurred, investigate it in the console")

    context = {
        'publishKey': publishKey,
        'selected_membership': selected_membership
    }

    return render(request, "memberships/membership_payment.html", context)

@login_required
def updateTransactionRecords(request, subscription_id):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)
    user_membership.membership = selected_membership
    user_membership.save()

    sub, created = Subscription.objects.get_or_create(
        user_membership=user_membership)
    sub.stripe_subscription_id = subscription_id
    sub.active = True
    sub.save()

    try:
        del request.session['selected_membership_type']
    except:
        pass

    messages.info(request, 'Successfully created {} membership'.format(
        selected_membership))
    return redirect(reverse('memberships:select'))

@login_required
def cancelSubscription(request):
    user_sub = get_user_subscription(request)

    if user_sub.active is False:
        messages.info(request, "You dont have an active membership")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    sub = stripe.Subscription.retrieve(user_sub.stripe_subscription_id)
    sub.delete()

    user_sub.active = False
    user_sub.save()

    free_membership = Membership.objects.get(membership_type='Free')
    user_membership = get_user_membership(request)
    user_membership.membership = free_membership
    user_membership.save()

    messages.info(
        request, "Successfully cancelled membership. We have sent an email")
    # sending an email here

    return redirect(reverse('memberships:select'))
