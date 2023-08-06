# HouseQuest 🏠

HouseQuest is a web-based platform that connects landlords with potential tenants, streamlining the rental process for both parties. Landlords can list their vacant properties, while tenants can search for rentals based on their preferences and easily contact landlords for inquiries, bookings and rent payments.

### 🔧 Tools and technologies used
1. Django
2. HTML5
3. CSS, Tailwind CSS
4. JavaScript
5. SQLite
6. Daraja API
7. Ngrok

### 🌟 Features
* __User accounts__: Both landlords and tenants can register and log into the system to manage their rental properties or search for available rentals.
* __Property listings__: Landlords can add posts about their available rentals, including details such as the number of vacancies per listing, location and pricing details.
* __Customizable search__: Tenants can customize their search criteria based on their specific needs, such as price range, location and type of listing.
* __Communication__: The system provides a means of communication between tenants and landlords.
* __Payments__: Tenants can send booking fees and pay rent through the platform.
* __Admin dashboard__: The admin can view summary details of the platform’s usage and activity in the form of images and tables.

### 💻 Running the project
1. Install Python from [the official website](https://www.python.org/downloads/).
2. Install Django by running `pip install django`.
3. Clone this repository or download the source code.
4. Set up the database by running `python manage.py makemigrations` and `python manage.py migrate`.
5. Create an admin user by running `python manage.py createsuperuser` and following the prompts.
6. Run the development server by running `python manage.py runserver`. Access it by navigating to `http://127.0.0.1:8000/` in your web browser.
7. (Optional) Install ngrok to expose your local development server to the internet for testing callback URLs.


### 💡 Additional tips for admins
* To add a new listing type:
  1. In the Django admin panel, navigate to the `Listing Types` section and click on the `Add Listing Type` button.
  2. Fill in the required information for the new listing type and click on the `Save` button.
* To grant a user admin privileges(viewing the admin dashboard):
  1. Create a new user by following the normal user registration process.
  2. In the Django admin panel, navigate to the `Users` section and find the newly created user. Click on their username to view their           details.
  3. In the user details page, check the `is_admin` checkbox to grant the user admin privileges and uncheck both `is_landlord` and `is_tenant`.
  4. The new admin user will now be able to view the admin summaries of the website.
  5. (Optional) Make sure to tick `is_admin` for the original admin user to avoid displaying them in the list of users in summaries.
