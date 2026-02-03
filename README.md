# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)








############################################



### SETUP & RUN

##Backend Setup

open command promt

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates tables + default users)
python init_db.py

# Run server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000


###  Frontend Setup

# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm start




##############################3


STEP-BY-STEP FIX (DO EXACTLY THIS)
Confirm Python 3.11 is installed

Open a new terminal (important):

python --version


You MUST see:

Python 3.11.x


If not, stop and tell me.

Find Python 3.11 path
where python


You should see something like:

C:\Program Files\Python311\python.exe


We will use this explicitly.

Delete the broken virtual environment

From backend folder:

rmdir /s /q venv

4️⃣ Create venv using Python 3.11 explicitly

(VERY IMPORTANT)

"C:\Program Files\Python311\python.exe" -m venv venv


If your path is slightly different, adjust it based on where python.

Activate venv
venv\Scripts\activate


Verify:

python --version


You MUST see:

Python 3.11.x


If you still see 3.14 → stop immediately.

Upgrade pip
python -m pip install --upgrade pip

Install requirements
pip install -r requirements.txt


Verify SQLAlchemy
python -c "import sqlalchemy; print(sqlalchemy.__version__)"


Expected:

2.0.25

Run DB init
python init_db.py



################
 Admin created: admin@offerzone.com / Admin@123
 User created: user@offerzone.com / User@123



###########


Go to the frontend folder

Open a new terminal:

cd C:\Praneeth\Training\OFFERZONE\OfferZone\ecommerce-scraper\frontend

2️Install Bootstrap Icons
npm install bootstrap-icons


or (if you use yarn):

yarn add bootstrap-icons

3️Verify the import path (IMPORTANT)

Open:

frontend/src/index.js


Make sure you have exactly this:

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';


This path is correct only if bootstrap-icons is installed.

4️ Restart React dev server

Stop the server (Ctrl + C), then:

npm start


or

npm run dev








###############

PS C:\WINDOWS\System32> cd C:\Praneeth\Training\OFFERZONE\OfferZone\ecommerce-scraper\backend
PS C:\Praneeth\Training\OFFERZONE\OfferZone\ecommerce-scraper\backend> venv\Scripts\activate
(venv) PS C:\Praneeth\Training\OFFERZONE\OfferZone\ecommerce-scraper\backend> python -m uvicorn main:app --reload




###########



cd frontend
npm install react-plotly.js plotly.js





npm install recharts  -- froentend

cd frontend
npm install recharts react-router-dom


<img width="1919" height="1020" alt="image" src="https://github.com/user-attachments/assets/82cb21e9-990d-451f-bbcf-d7f1be195efa" />

