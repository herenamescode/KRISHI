// ========================================
// CHATBOT FUNCTIONALITY
// ========================================

class KrishiChatbot {
    constructor() {
        this.responses = {
            // Greetings
            greetings: {
                keywords: ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'],
                responses: [
                    'Hello! 🌾 Welcome to Krishi. How can I help you with your farming needs today?',
                    'Hi there! 👋 I\'m here to help you with crop recommendations and disease detection. What would you like to know?',
                    'Greetings! 🌱 Ask me anything about crops, diseases, or how to use Krishi!'
                ]
            },
            
            // Crop Prediction
            cropPrediction: {
                keywords: ['crop', 'predict', 'recommendation', 'what crop', 'which crop', 'best crop', 'should i plant'],
                responses: [
                    'I can help you predict the best crop! 🌾 Go to the "Crop Recommendation" section and enter your soil parameters (N, P, K, pH) and climate data (temperature, humidity, rainfall). Our AI will recommend the optimal crop for your conditions!',
                    'To get crop recommendations, scroll to the Crop Prediction section above. You\'ll need to provide soil nutrients (Nitrogen, Phosphorus, Potassium) and climate information. Try it out! 🌱'
                ]
            },
            
            // Disease Detection
            diseaseDetection: {
                keywords: ['disease', 'sick', 'infected', 'leaf', 'plant problem', 'unhealthy', 'spots on leaves'],
                responses: [
                    'I can help detect plant diseases! 🔬 Head to the "Disease Detection" section, select your crop type (corn, rice, or wheat), and upload a clear photo of the affected leaf. Our AI will identify the disease and suggest treatment!',
                    'For disease detection, go to the Disease Detection section above. Choose your crop type and upload a leaf image. We support corn, rice, and wheat disease detection! 📷'
                ]
            },
            
            // Soil Information
            soilInfo: {
                keywords: ['soil', 'npk', 'nitrogen', 'phosphorus', 'potassium', 'ph', 'soil test'],
                responses: [
                    'Soil health is crucial! 🌍 You need to know your soil\'s NPK values (Nitrogen, Phosphorus, Potassium) and pH level. Get a soil test done at your local agricultural extension office. Typical values: N: 0-140, P: 5-145, K: 5-205, pH: 3.5-9.5',
                    'NPK stands for Nitrogen (N), Phosphorus (P), and Potassium (K) - the three essential nutrients for plant growth. You can get your soil tested at agricultural labs. The pH level indicates soil acidity/alkalinity. Most crops prefer pH 6-7. 🧪'
                ]
            },
            
            // Climate/Weather
            climate: {
                keywords: ['weather', 'climate', 'temperature', 'humidity', 'rainfall', 'rain'],
                responses: [
                    'Climate factors are important for crop selection! ☀️ Our system considers temperature (°C), humidity (%), and rainfall (mm). You can get this data from local weather stations or online weather services. Different crops thrive in different climates!',
                    'Weather data helps predict the best crops! 🌦️ Temperature affects plant growth, humidity impacts disease risk, and rainfall determines irrigation needs. Input your local climate data for accurate recommendations!'
                ]
            },
            
            // Corn/Maize
            corn: {
                keywords: ['corn', 'maize'],
                responses: [
                    'Corn (maize) is a major cereal crop! 🌽 Common diseases include: Common Rust (orange/brown pustules), Northern Leaf Blight (grayish lesions), and Cercospora Leaf Spot. Upload a leaf image in the Disease Detection section for diagnosis!',
                    'Growing corn? 🌽 It needs: Temperature: 20-30°C, Good drainage, pH 5.8-7.0. Watch out for rust and blight diseases. Use our disease detection tool to identify any problems early!'
                ]
            },
            
            // Rice/Paddy
            rice: {
                keywords: ['rice', 'paddy'],
                responses: [
                    'Rice is a staple crop! 🍚 Common diseases: Bacterial Leaf Blight (yellow to white lesions), Brown Spot (brown spots with yellow halo), Leaf Smut (black lesions). Upload images to detect diseases early!',
                    'Rice cultivation tips: 🌾 Requires: 20-35°C temperature, high humidity (70-80%), lots of water. Common issues include blast, blight, and smut. Use our AI to detect diseases quickly!'
                ]
            },
            
            // Wheat
            wheat: {
                keywords: ['wheat'],
                responses: [
                    'Wheat is a major grain crop! 🌾 Watch for rust diseases: Brown Rust (brown pustules on leaves) and Yellow Rust (yellow-orange pustules in stripes). Early detection is key - use our disease detection tool!',
                    'Growing wheat? 🌾 Optimal conditions: 15-25°C, moderate rainfall (40-100cm annually), pH 6.0-7.5. Rust diseases are common - upload leaf photos for quick diagnosis and treatment advice!'
                ]
            },
            
            // How to use
            howToUse: {
                keywords: ['how to use', 'how does it work', 'guide', 'tutorial', 'help me', 'instructions'],
                responses: [
                    'Using Krishi is easy! 📝 For Crop Prediction: Enter your soil and climate data, click "Predict Best Crop". For Disease Detection: Choose crop type, upload leaf photo, click "Analyze Disease". Both features give instant results!',
                    'Here\'s how to use Krishi: 1️⃣ Crop Prediction - Fill in the form with your parameters. 2️⃣ Disease Detection - Select crop, upload image. 3️⃣ Get AI-powered results instantly! Scroll up to try either feature! ✨'
                ]
            },
            
            // Accuracy
            accuracy: {
                keywords: ['accurate', 'accuracy', 'reliable', 'trust', 'correct'],
                responses: [
                    'Our AI models are trained on thousands of samples! 🎯 Crop prediction uses Random Forest with 95%+ accuracy. Disease detection uses Convolutional Neural Networks with high accuracy. However, always consult agricultural experts for critical decisions!',
                    'Krishi uses state-of-the-art machine learning! 🧠 Our models are highly accurate but should be used as a support tool. For best results: provide accurate data, take clear photos, and verify with local agricultural experts!'
                ]
            },
            
            // Treatment/Solution
            treatment: {
                keywords: ['treatment', 'cure', 'solution', 'fix', 'remedy', 'what to do'],
                responses: [
                    'For treatment advice, use our Disease Detection tool! 💊 It provides specific recommendations for each disease. General tips: Remove infected parts, improve air circulation, use appropriate fungicides, and maintain proper nutrition!',
                    'Treatment depends on the disease! 🏥 Upload a leaf image to get specific recommendations. Prevention is key: proper spacing, good drainage, crop rotation, and regular monitoring. Our AI gives tailored advice for detected diseases!'
                ]
            },
            
            // Fertilizer
            fertilizer: {
                keywords: ['fertilizer', 'fertiliser', 'nutrients', 'feeding', 'manure'],
                responses: [
                    'Fertilizers provide essential nutrients! 🌱 NPK fertilizers supply Nitrogen (leaf growth), Phosphorus (roots/flowers), and Potassium (overall health). Apply based on soil test results. Our crop recommendation considers your soil\'s current NPK levels!',
                    'Use fertilizers wisely! ⚗️ Over-fertilizing harms crops and environment. Get a soil test first. Organic options: compost, manure. Chemical: NPK fertilizers based on soil needs. Our system helps you choose crops that match your soil\'s nutrients!'
                ]
            },
            
            // Thanks
            thanks: {
                keywords: ['thank', 'thanks', 'appreciate', 'helpful'],
                responses: [
                    'You\'re welcome! 😊 Happy farming! Feel free to ask anything else about crops or diseases. Good luck with your harvest! 🌾',
                    'Glad I could help! 🌟 Remember, I\'m always here if you have more questions. Wishing you a bountiful harvest! 🌾✨',
                    'My pleasure! 🙌 Don\'t hesitate to ask if you need more help. Happy farming with Krishi! 🌱'
                ]
            },
            
            // Goodbye
            goodbye: {
                keywords: ['bye', 'goodbye', 'see you', 'exit', 'quit'],
                responses: [
                    'Goodbye! 👋 Come back anytime you need agricultural advice. Happy farming! 🌾',
                    'Take care! 🌟 Wishing you great harvests. Feel free to return whenever you need help! 🌱',
                    'See you later! 👨‍🌾 May your crops be healthy and your yields abundant! 🌾'
                ]
            },
            
            // About Krishi
            about: {
                keywords: ['what is krishi', 'about krishi', 'about this', 'what is this'],
                responses: [
                    'Krishi is an AI-powered smart agriculture platform! 🌾 We help farmers make data-driven decisions with two main features: Crop Recommendation (suggests best crops based on soil/climate) and Disease Detection (identifies plant diseases from photos). All powered by machine learning!',
                    'Welcome to Krishi! 🌱 We combine traditional farming wisdom with modern AI. Our platform predicts optimal crops using Random Forest algorithms and detects diseases using deep learning. It\'s free, fast, and designed to help farmers succeed! 🎯'
                ]
            }
        };
    }

    // Find matching response based on user input
    getResponse(userInput) {
        const input = userInput.toLowerCase().trim();
        
        // Check each category
        for (let category in this.responses) {
            const data = this.responses[category];
            
            // Check if any keyword matches
            for (let keyword of data.keywords) {
                if (input.includes(keyword)) {
                    // Return random response from the category
                    const randomIndex = Math.floor(Math.random() * data.responses.length);
                    return data.responses[randomIndex];
                }
            }
        }
        
        // Default response if no match found
        return this.getDefaultResponse(input);
    }

    // Default response for unmatched queries
    getDefaultResponse(input) {
        const defaultResponses = [
            'I\'m not sure about that. 🤔 But I can help you with: crop recommendations, disease detection, soil info, weather data, or how to use Krishi. What would you like to know?',
            'Hmm, I didn\'t quite understand that. 💭 Try asking about: predicting crops, detecting diseases, soil nutrients, or general farming advice!',
            'That\'s interesting! 🌾 I specialize in crop prediction and disease detection. Ask me about soil parameters, plant diseases, or how to use the platform!',
            'I\'m still learning about that! 📚 I\'m best at helping with crop recommendations, disease identification, and farming basics. What can I help you with?'
        ];
        
        const randomIndex = Math.floor(Math.random() * defaultResponses.length);
        return defaultResponses[randomIndex];
    }
}

// Initialize chatbot
const krishiBot = new KrishiChatbot();

// ========================================
// CHATBOT UI FUNCTIONALITY
// ========================================

let isChatOpen = false;

// Toggle chat window
function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    const chatButton = document.getElementById('chatButton');
    
    isChatOpen = !isChatOpen;
    
    if (isChatOpen) {
        chatWindow.style.display = 'flex';
        chatButton.style.transform = 'scale(0.9)';
        
        // Add welcome message if chat is empty
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer.children.length === 0) {
            addBotMessage('Hello! 👋 I\'m Krishi Bot. Ask me anything about crop prediction, disease detection, or farming advice!');
        }
    } else {
        chatWindow.style.display = 'none';
        chatButton.style.transform = 'scale(1)';
    }
}

// Send message
function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (message === '') return;
    
    // Add user message
    addUserMessage(message);
    
    // Clear input
    input.value = '';
    
    // Get bot response
    setTimeout(() => {
        const response = krishiBot.getResponse(message);
        addBotMessage(response);
    }, 500);
}

// Add user message to chat
function addUserMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message user-message';
    messageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot-message';
    messageDiv.innerHTML = `
        <div class="message-avatar">🌾</div>
        <div class="message-content">${message}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Scroll chat to bottom
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle Enter key in chat input
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

// Quick suggestions
function useSuggestion(suggestion) {
    document.getElementById('chatInput').value = suggestion;
    sendMessage();
}