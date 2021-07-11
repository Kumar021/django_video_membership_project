from allauth.account.forms import LoginForm, SignupForm

##ref https://gavinwiener.medium.com/modifying-django-allauth-forms-6eb19e77ef56

class MyCustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super(MyCustomLoginForm, self).__init__(*args, **kwargs)
        # for fieldname, field in self.fields.items():
        #     field.widget.attrs.update({
        #         'class': 'form-control'
        #     })
        self.fields['login'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control'
        })

    # def login(self, *args, **kwargs):

    #     # Add your own processing here.

    #     # You must return the original result.
    #     return super(MyCustomLoginForm, self).login(*args, **kwargs) 



class MyCustomSignupForm(SignupForm):
    
    def __init__(self, *args, **kwargs):
        super(MyCustomSignupForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
    
    # def save(self, request):
    #     organization = self.cleaned_data.pop('organization')
    #     ...
    #     user = super(MyCustomSignupForm, self).save(request)





