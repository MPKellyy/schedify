import webapp2
import os
import jinja2
from google.appengine.api import users
from models import SchedifyUser, Connect, Event, Attendance

the_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class LandingHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    # If the user is logged in...
    if user:
      signout_link_html = '<a href="%s">sign out</a>' % (
          users.create_logout_url('/'))
      email_address = user.nickname()
      schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()
      # If the user is registered...
      if schedify_user:
        # Enter home page here:
        # Enter the page that the user sees after they have signed in
        # Greet them with their personal information

        # Home Handler
        user = users.get_current_user()
        email_address = user.nickname()
        email_list = email_address.split('@')
        email_start = email_list[0]

        signout_link = users.create_logout_url('/')

        home_data = {
            "emailStart": email_start,
            "sign_out": signout_link,
            "first_name": schedify_user.first_name,
            "last_name":schedify_user.last_name,
            "friend_list": schedify_user.friends
        }
        home_template = the_jinja_env.get_template('templates/home.html')
        self.response.write(home_template.render(home_data))

        #  Coding to know
        # self.response.write('''
        #     ENTER HOME PAGE TEMPLATE HERE! <br>Welcome %s %s (%s)! <br> %s <br>''' % (
        #       schedify_user.first_name,
        #       schedify_user.last_name,
        #       email_address,
        #       signout_link_html))
      # If the user isn't registered...
      else:
        # Offer a registration form for a first-time visitor:
        sign_up_template = the_jinja_env.get_template('templates/sign-up.html')
        signout_link = users.create_logout_url('/')
        sign_up_data = {
            "sign_out": signout_link
        }
        self.response.write(sign_up_template.render(sign_up_data))
    else:
      # If the user isn't logged in...
      landing_template = the_jinja_env.get_template('templates/landing.html')
      login_url = users.create_login_url('/')
      landing_data = {
        "login": login_url,
      }
      # Prompt the user to sign in.
      self.response.write(landing_template.render(landing_data))

  def post(self):
    # Enter home page here:
    # Enter the page that the user sees after they have signed in
    user = users.get_current_user()
    username = self.request.get('user_name')
    firstname = self.request.get('first_name')
    lastname = self.request.get('last_name')

    schedify_user = SchedifyUser(
        first_name = firstname,
        last_name = lastname,
        username = username,
        friends = [],
        email=user.nickname())
        #email=self.request.get('email')) because i want to parse their email to get their cal
    schedify_user.put()
    welcome_template = the_jinja_env.get_template('templates/welcome.html')
    welcome_data = {
        "first_name": firstname,
        "last_name": lastname
    }
    self.response.write(welcome_template.render(welcome_data))
class ScheduleHandler(webapp2.RequestHandler):
    def get(self):
        welcome_template = the_jinja_env.get_template('templates/schedule.html')
        user = users.get_current_user()
        email_address = user.nickname()
        email_list = email_address.split('@')
        email_start = email_list[0]
        schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()

        welcome_data = {
            "emailStart": email_start,
            "friend_list": schedify_user.friends,
            "friendIndex":0,
            "friendEmailStart": None
        }
        self.response.write(welcome_template.render(welcome_data))
    def post(self):
        welcome_template = the_jinja_env.get_template('templates/schedule.html')
        welcome_data = {
            "first_name": firstname,
            "last_name": lastname
        }
        self.response.write(welcome_template.render())

class EventFeedHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        email_address = user.nickname()
        schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()

        user = users.get_current_user()
        email_address = user.nickname()
        schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()

        event_ownership = self.request.get('event-type')


        friends_key_list = schedify_user.friends
        users_key = [schedify_user.key]
        users_key.extend(friends_key_list)

        event_list = []
        for user_key in users_key:
            events = Event.query(Event.owner == user_key).fetch()
            event_list.extend(events)

        event_template = the_jinja_env.get_template('templates/event-feed.html')

        event_data = {
            # "newevent_url": new_event,
            "event_info": event_list
        }
        self.response.write(event_template.render(event_data))

    def post(self):
        user = users.get_current_user()
        email_address = user.nickname()
        schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()

        event_ownership = self.request.get('event-type')

        if event_ownership == "self":
            event_list = Event.query(Event.owner == schedify_user.key).fetch()
        elif event_ownership == "friends":
            friends_key_list = schedify_user.friends
            event_list = []
            for friend_key in friends_key_list:
                events = Event.query(Event.owner == friend_key).fetch()
                event_list.extend(events)
        elif event_ownership == "all":
            friends_key_list = schedify_user.friends
            users_key = [schedify_user.key]
            users_key.extend(friends_key_list)

            event_list = []
            for user_key in users_key:
                events = Event.query(Event.owner == user_key).fetch()
                event_list.extend(events)

        event_template = the_jinja_env.get_template('templates/event-feed.html')

        event_data = {
            "event_info": event_list
        }
        self.response.write(event_template.render(event_data))

class EventHandler(webapp2.RequestHandler):
    def get(self):
        event_template = the_jinja_env.get_template('templates/event.html')

        event_data = {

        }

        self.response.write(event_template.render(event_data))

class NewEventHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
          email_address = user.nickname()
          schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()
          if schedify_user:
            newevent_template = the_jinja_env.get_template('templates/newevent.html')
            self.response.write(newevent_template.render())
            return
        self.error(403)
        return
    def post(self):
        # create new event?
        # look at the sign in if statement
        # grab the email adress through google users api then search
        #   for schedify through that email address
        newevent_template = the_jinja_env.get_template('templates/newevent.html')

        user = users.get_current_user()
        email_address = user.nickname()
        schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()

        schedify_event = Event(
            owner = schedify_user.key,
            title = self.request.get('event_title'),
            summary = self.request.get('event_summary'),
            exclusives = [],
            attending = [],
            not_attending = []
        )

        schedify_event.put()
        # Add later when you add the home page html and link it to this page
        #       You need to make sure you can call a user that is loged in
        #
        # schedify_attendance = Attendance (
        #      user =
        #      event = schedify_event,
        # )
        self.response.write(newevent_template.render())

class ConnectionsHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        email_address = user.nickname()
        schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()
        connections_template = the_jinja_env.get_template('templates/connections.html')

        connections_data = {
            "friend_list": schedify_user.friends,
            "requestkey_list": schedify_user.requests
        }
        self.response.write(connections_template.render(connections_data))

    # this shows the list of users who match that username
    def post(self):
        user = users.get_current_user()
        email_address = user.nickname()
        schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()
        connections_template = the_jinja_env.get_template('templates/connections.html')
        resolve_request = self.request.get('request_answer')
        if resolve_request == "Accept":
            requester = self.request.get('request_user')
            schedify_user.add_friend(requester)
            requester.add_friend(schedify_user.key)
        elif resolve_request == "Decline":
            schedify_user.remove_request(requester)
        connections_data = {
            "friend_list": schedify_user.friends,
            "requestkey_list": schedify_user.requests
        }
        self.response.write(connections_template.render(connections_data))

class ProfileHandler(webapp2.RequestHandler):
    # your profile
    def get(self):
        profile_template = the_jinja_env.get_template('templates/profile.html')
        user = users.get_current_user()
        email_address = user.nickname()
        schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()

        profile_data = {
            "user_name": schedify_user.username,
            "first_name": schedify_user.first_name,
            "last_name": schedify_user.last_name,
            "account": "self"
        }
        self.response.write(profile_template.render(profile_data))

    # user profile lookup
    def post(self):
        profile_template = the_jinja_env.get_template('templates/profile.html')
        user = users.get_current_user()
        email_address = user.nickname()
        schedify_user = SchedifyUser.query().filter(SchedifyUser.email == email_address).get()

        # there should only be one username per account
        username_search = self.request.get('username_search')
        user_search = SchedifyUser.query(SchedifyUser.username == username_search).get()

        # checks to see if user is passing in their own Account
        if user_search == schedify_user:
            account_status = "self"
            friend_status = None
            request_status = None
        else:
            account_status = "other"
            friend_status = self.request.get('friend_status')
            request_status = False

            # if button to add/remove friend was cliked launch this code
            if (friend_status == "add friend"):
                request_status = True
                user_search.add_request(schedify_user.key)
            elif (friend_status == "remove friend"):
                schedify_user.remove_friend(user_search.key)
                user_search.remove_friend(schedify_user.key)
                request_status = False
            elif (friend_status == "request"):
                user_search.remove_request(schedify_user.key)
                request_status = False

            # checks if profile is part of friends group
            friend_status = False

            for friend_key in schedify_user.friends:
                if friend_key == user_search.key:
                    friend_status = True

            # check if you requested a connections
            for request_key in user_search.requests:
                if request_key == schedify_user.key:
                    request_status = True



        profile_data = {
            "user_name": user_search.username,
            "first_name": user_search.first_name,
            "last_name": user_search.last_name,
            "friend_status": friend_status,
            "request_status": request_status,
            "account": account_status
        }
        self.response.write(profile_template.render(profile_data))


app = webapp2.WSGIApplication([
    ('/', LandingHandler),
    # schedule page should be connected to home page
    ('/schedule', ScheduleHandler),
    ('/event-feed', EventFeedHandler),
    ('/new_event', NewEventHandler),
    ('/event', EventHandler),
    ('/connections', ConnectionsHandler),
    ('/profile', ProfileHandler)

], debug=True)
