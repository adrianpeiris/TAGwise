# **TAGwise: Machine Learning-Based Bookmark Aggregator**

## 🚀 Overview

**TAGwise** is an intelligent **Bookmark Manager** that uses **Machine Learning** and **Natural Language Processing (NLP)** to **automatically categorize** bookmarks collected from **social media platforms** like **YouTube**, **Reddit**, and **Twitter**.

🧠 **What it does:**
- Automatically **categorizes bookmarks** (e.g., "Work", "Education", "Entertainment").
- **Fetches bookmarks** from **YouTube**, **Reddit**, **Twitter**.
- **Seamlessly integrates** with a **Chrome extension** for instant bookmarking and categorization.
- **User-friendly interface** to **search, filter,** and **manage** your bookmarks!

## 🌟 Key Features

- **Automatic Categorization:** Machine learning categorizes content into predefined groups (e.g., Work, Education, Entertainment).
- **API Integration:** Fetch bookmarks from **YouTube**, **Reddit**, **Twitter**.
- **Chrome Extension:** Quickly add and categorize bookmarks from any webpage.
- **Search & Filtering:** Effortlessly find saved bookmarks via the dashboard.
- **Personalized User Control:** Edit, add, or delete tags and categories.

## 🛠️ Technology Stack

- **Backend:** Python, Flask
- **Machine Learning:** XGBoost, scikit-learn
- **Frontend:** HTML, CSS, JavaScript (for Chrome extension)
- **Database:** MySQL (for bookmark storage)
- **Data Processing:** pandas, NumPy
- **Visualization:** Matplotlib, Seaborn

## 🏗️ How It Works

### 1. **Collect Data**
   - The system collects data via **API integration** from **YouTube**, **Reddit**, and **Twitter**. For non-API sources, it uses **web scraping**.

### 2. **Preprocess and Clean Data**
   - We clean the data by removing **special characters**, **emojis**, and **missing values.**  
   - The text is **combined** (title + description) and transformed into **numerical features** using **TF-IDF**.

### 3. **Train the Model**
   - A machine learning model (**XGBoost**) is trained to categorize the content into predefined categories (e.g., "Work", "Education").
   - The model uses the **TF-IDF vectorizer** to convert text into features that can be processed by the algorithm.

### 4. **Categorize and Save**
   - Once trained, the model **automatically categorizes** new bookmarks and saves them to the database.
   - Users can manage bookmarks via the **web app** and **Chrome extension**.

---

## 🔧 Testing the System

### 🎯 Try it out with a Test Bookmark:

1. Visit the web app (on [http://localhost:5000](http://localhost:5000)).
2. **Click "Add New Bookmark"** and paste any URL.
3. TAGwise will automatically analyze and categorize the bookmark.
4. You can then **search, filter,** and **edit tags**.

---

## 📈 Model Evaluation

We evaluated the model using **Accuracy, Precision, Recall, and F1-Score**.  
### **XGBoost Model Performance:**
- **Best Performing Model**: Highest accuracy and balanced performance between precision and recall.

---

## ⚙️ Challenges Faced

- **API Limitations**: Some platforms, like YouTube, had **rate limits** and access restrictions. **Web scraping** was used to fill the gaps.
- **Data Quality**: Missing or inconsistent metadata required robust preprocessing.
- **Model Performance**: **Imbalanced categories** led to lower accuracy in minority classes.

---

## 💡 Lessons Learned

- **Data preparation** is crucial for good **model accuracy**.  
- **API integration** requires handling **rate limits** properly.
- **Model selection**: **Ensemble methods** (like **XGBoost**) and **ANN** work better for complex tasks than simpler models like **Logistic Regression**.

---

## 🚀 Future Work

- **Multi-platform integration** (e.g., Instagram, LinkedIn).
- **Cloud deployment** for scalability and ease of access.
- **User login** system for personalized bookmark management.

---

## 📚 References

- [Kaggle: Natural Language Processing Datasets](https://www.kaggle.com/)
- [Twitter Developer Documentation](https://developer.twitter.com/en/docs)
- [YouTube API Documentation](https://developers.google.com/youtube/)
- [Reddit API Documentation](https://www.reddit.com/dev/api/)

---

### 👨‍💻 Contact

- If you have any questions or suggestions, please open an **issue** or contact me directly via **GitHub**.

---

This **README** now has:
- Clear **installation** and **usage instructions**.
- **Key features** and **model performance** for easy reference.
- **Testing examples** to engage users quickly.

Let me know if you need more changes! 🚀
