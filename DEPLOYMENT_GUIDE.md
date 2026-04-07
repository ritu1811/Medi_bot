# Production Deployment Guide: MEDI_BOT

Now that your local AI Medical Bot is flawlessly built, you can transition it from your local Windows machine to the internet so that anyone across the globe can safely access it.

Below are the exact steps to deploy your application professionally using **Render** (a very popular, easy-to-use cloud host for Python applications), completely for free.

---

## Step 1: Security & Setup (Gunicorn)
Flask's native `app.run()` is built for development, not internet-level traffic. When deploying, you need an enterprise web server like **Gunicorn**.

1. **Add Gunicorn to Requirements**
   Open your `requirements.txt` and append this exact text to the bottom:
   ```text
   gunicorn==21.2.0
   ```

2. **Verify your API Keys**
   Ensure your `.env` file looks exactly like this, BUT ensure you do **NOT** upload it to Github. You will paste these keys securely into the Render platform instead.
   ```text
   PINECONE_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   ```

## Step 2: Push your Code to GitHub
Cloud services pull your source code directly from GitHub to host it.

1. Create a free account on [GitHub](https://github.com/).
2. Create a **New Repository** (make it Private to protect any stray API keys!).
3. Upload all your files inside `G-medi` (including `app.py`, `requirements.txt`, `src/`, `templates/`, etc.) **except** your `.env` file and `.venv` folder!

## Step 3: Deploy on Render
1. Go to [Render.com](https://render.com/) and sign up using your GitHub account.
2. Click **New +** and select **Web Service**.
3. Connect the GitHub repository you just created.
4. Render will ask for your configuration settings. Fill them out exactly like this:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

## Step 4: Inject your API Keys (Environment Variables)
Your code uses `load_dotenv()` to grab your Pinecone and Gemini credentials. Since you didn't upload your `.env` file to Github (for security), you need to inject them into Render directly.

1. On the Render Dashboard for your new app, scroll down to the **Environment** section > **Environment Variables**.
2. Click `Add Environment Variable` and type exactly:
   - **Key:** `GOOGLE_API_KEY` | **Value:** `AIzaSy...` (your new key)
3. Click `Add Environment Variable` again:
   - **Key:** `PINECONE_API_KEY` | **Value:** `pcsk_...` (your Pinecone key)
4. Click **Save**.

## Step 5: Launch!
Scroll to the top of Render and click **Deploys** > **Manual Deploy**.
Render will grab your code, install your libraries from `requirements.txt`, boot up Gunicorn, and give you a public `https://...` link.

*Done! Your modern, AI-powered Medical Assistant is now safely live on the internet!*
