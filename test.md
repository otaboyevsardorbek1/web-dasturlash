# WebSocket Chat Dasturi uchun Mukammal LLM Prompt Template

## 📋 **LOYHA UMUMIY TA'RIFI (Context)**

```
Siz WebSocket texnologiyasi asosida real vaqtli chat ilovasini yaratish ustida ishlayapsiz. 
Dastur hozirgi holatda:

1. **Backend:** Python Flask + Flask-SocketIO
2. **Frontend:** HTML, CSS, JavaScript + Socket.IO client
3. **Funksiyalar:**
   - Real vaqtli xabar almashish
   - Foydalanuvchi nomi avtomatik generatsiya
   - Vaqt ko'rsatish (HH:MM)
   - Typing indikatori
   - Foydalanuvchilar soni
   - Responsive dizayn

Loyha yangi funksiyalar qo'shish va mukammallashtirish uchun rivojlantirilmoqda.
```

## 🎯 **ASOSIY PROMPT STRUKTURASI**

### **1. Kod Yozish uchun Prompt**
```
MENGA KOD YOZISHGA YORDAM BERA OLASANMI?

**Loyha tafsilotlari:**
- Dastur turi: Real vaqtli WebSocket chat dasturi
- Backend: Python Flask + Flask-SocketIO
- Frontend: HTML/CSS/JavaScript
- Maqsad: [BU YERGA ANIQ MAQSAD YOZING]

**Menga kerak:**
- [Funksiya nomi] funksiyasini qo'shish kerak
- [Texnologiya/kutubxona] dan foydalanish kerak
- [Xususiyat] mavjud kodga integratsiya qilish kerak

**Misol:**
Menga chat dasturiga fayl yuklash funksiyasini qo'shish kerak. 
Foydalanuvchilar rasm, PDF va boshqa fayllarni yuklay olishi kerak. 
Flask backend da buni qanday qilishim mumkin?
```

### **2. Xatolarni Tuzatish uchun Prompt**
```
MENGA BU XATOLIKNI TUZATISHGA YORDAM BERA OLASANMI?

**Xatolik haqida:**
- Xatolik matni: [XATOLIK MATNINI KO'CHIRIB QO'YING]
- Qachon paydo bo'ladi: [HARAKAT/SHARTNI TASVIRLANG]
- Kod qismi: [RELEVANT KODNI KO'CHIRING]

**Mening tahlilim:**
- Menimcha xatolik sababi: [TAHLILINGIZ]
- Men shunday deb o'ylayman: [TAHMININGIZ]

**Menga kerak:**
- Xatolikning aniq sababi
- To'g'ri yechim
- Oldini olish usullari
```

### **3. Loyhani Kengaytirish uchun Prompt**
```
MENGA LOYHANI KENGAYTIRISHGA YORDAM BERA OLASANMI?

**Joriy holat:**
- Dastur: WebSocket chat dasturi
- Texnologiya stack: [Hozirgi texnologiyalar ro'yxati]
- Mavjud funksiyalar: [Funksiyalar ro'yxati]

**Qo'shmoqchi bo'lgan funksiya:** [YANGI FUNKSIYA NOMI]

**Tafsilotlar:**
- Bu funksiya nima qiladi: [TAFSILOTLI TAVSIF]
- Nega kerak: [MUAMMO/YECHIM]
- Qanday ishlashi kerak: [ISHLOV CHIZMASI]

**Texnik talablar:**
- Backend o'zgarishlar: [Python/Flask o'zgarishlari]
- Frontend o'zgarishlar: [HTML/JS o'zgarishlari]
- Database (agar kerak bo'lsa): [DB o'zgarishlari]

**Misol:**
Menga chat dasturiga video suhbat funksiyasini qo'shish kerak.
WebRTC texnologiyasidan foydalanishim kerak.
Qanday bosqichlar bilan bajarishim mumkin?
```

## 🔧 **MAXSUS FUNKSIYALAR UCHUN PROMPT NAMUNALARI**

### **1. Chat Xonalari (Rooms) qo'shish**
```
Menga chat dasturiga "chat xonalari" (rooms) funksiyasini qo'shish kerak.
Foydalanuvchilar turli mavzular uchun alohida xonalar yaratishi va ulanishi kerak.

**Talablar:**
1. Yangi xona yaratish imkoniyati
2. Mavjud xonalar ro'yxatini ko'rish
3. Xonaga kirish/chiqish
4. Har bir xona uchun alohida chat tarixi
5. Xona egasi va admin huquqlari

**Texnik talablar:**
- Backend: Flask-SocketIO rooms feature ishlatish
- Frontend: Xonalar paneli va chat oynasi
- Database: Xonalar va ularga tegishli xabarlarni saqlash

Qanday bosqichlarda bajarishim mumkin? Kod namunasi bilan tushuntiring.
```

### **2. End-to-End Encryption**
```
Menga chat xabarlarini end-to-end shifrlash (encryption) funksiyasini qo'shish kerak.
Faqat yuboruvchi va qabul qiluvchi xabarni o'qiy olsin.

**Talablar:**
1. Har bir foydalanuvchi uchun kalitlar juftligi (public/private)
2. Xabarlarni yuborishdan oldin shifrlash
3. Qabul qilgandan keyin deshifrlash
4. Kalitlarni xavfsiz saqlash
5. Forward secrecy ni ta'minlash

**Texnik talablar:**
- Python: PyCryptodome kutubxonasi
- JavaScript: Web Crypto API
- Kalitlar almashinuvi protokoli

Qanday amalga oshirishim mumkin? Kod strukturasini tushuntiring.
```

### **3. AI Assistant (ChatGPT integratsiyasi)**
```
Menga chat dasturiga AI assistant funksiyasini qo'shish kerak.
Foydalanuvchilar AI dan savol berishi va javob olishi mumkin.

**Talablar:**
1. /ai [savol] komandasi bilan ishlash
2. OpenAI API bilan integratsiya
3. Context ni saqlash (so'ngi 10 xabar)
4. Foydalanuvchilar uchun individual kontekst
5. AI javoblarini formatlash

**Texnik talablar:**
- Backend: OpenAI API bilan ulanish
- Frontend: AI xabarlarini alohida ko'rsatish
- Database: Kontekstni saqlash

Implementatsiya bosqichlarini tushuntiring.
```

### **4. Video Chat (WebRTC)**
```
Menga chat dasturiga real vaqtli video chat funksiyasini qo'shish kerak.
Foydalanuvchilar bir-biri bilan video orqali suhbatlashishi mumkin.

**Talablar:**
1. Video chaqiruvni boshlash
2. Video chaqiruvni qabul qilish/rad etish
3. Mikrofon va kamerani boshqarish
4. Ekran ulashish (screen sharing)
5. Video sifati sozlash

**Texnik talablar:**
- WebRTC texnologiyasi
- Signalling server (WebSocket)
- STUN/TURN serverlar
- Frontend: Media devices API

Arxitektura va kod namunasi bilan tushuntiring.
```

## 📊 **LOYHANI BOSHQARISH PROMPTLARI**

### **1. Project Planning**
```
Menga ushbu loyha uchun development roadmap yaratishga yordam bering.

**Loyha:** WebSocket Chat Dasturi
**Maqsad:** [LOYHA MAQSADI]
**Muddat:** [OXIRGI MUDDAT]

**Hozirgi holat:**
- Mavjud funksiyalar: [RO'YXAT]
- Texnik stack: [RO'YXAT]
- Jamoa: [SONI VA ROLLAR]

**Kerakli funksiyalar:**
1. [FUNKSIYA 1] - Muhimlik: [HIGH/MEDIUM/LOW]
2. [FUNKSIYA 2] - Muhimlik: [HIGH/MEDIUM/LOW]
3. [FUNKSIYA 3] - Muhimlik: [HIGH/MEDIUM/LOW]

Menga quyidagilarni tayyorlang:
1. Bosqichma-bosqich roadmap
2. Har bir bosqich uchun timeline
3. Resurslar talabi
4. Risk assessment
5. Success metrics
```

### **2. Code Review**
```
Menga ushbu kodni review qilishga yordam bering.

**Kod fayli:** [FAYL NOMI]
**Funksiya:** [FUNKSIYA NOMI]

**Kod:**
```python
[KODNI SHU YERGA PASTE QILING]
```

**Review uchun aspektlar:**
1. Performance optimallashtirish
2. Xavfsizlik (security)
3. Kod sifati (clean code)
4. Error handling
5. Scalability

Qaysi joylarni yaxshilashim mumkin? Takliflar bering.
```

### **3. Testing Strategy**
```
Menga chat dasturim uchun testing strategiyasini ishlab chiqishga yordam bering.

**Dastur turi:** Real vaqtli WebSocket chat
**Texnologiyalar:** Flask, Socket.IO, JavaScript
**Complexity:** [MURAKKABLIK DARAJASI]

**Test qilish kerak bo'lgan funksiyalar:**
1. WebSocket ulanishi
2. Xabar yuborish/qabul qilish
3. Foydalanuvchi boshqaruvi
4. [QO'SHIMCHA FUNKSIYALAR]

**Kerakli test turlari:**
- Unit testing
- Integration testing
- Load testing
- Security testing

Har bir test turi uchun framework va approach taklif qiling.
```

## 🚀 **LOYHANI PRODUCTIONGA TAYYORLASH**

### **1. Deployment Prompt**
```
Menga chat dasturini production serverga deploy qilishga yordam bering.

**Dastur tafsilotlari:**
- Backend: Python Flask + Socket.IO
- Frontend: Static HTML/CSS/JS
- Database: [AGAR BOR BO'LSA]
- Expected users: [FOYDALANUVCHILAR SONI]

**Deploy platformasi:** [DIGITALOCEAN/AWS/HEROKU/VPS]

**Talablar:**
1. Docker containerization
2. Nginx reverse proxy
3. SSL sertifikati (HTTPS)
4. Auto-restart on crash
5. Logging va monitoring

Step-by-step deployment guide berishingizni so'rayman.
```

### **2. Scaling Prompt**
```
Menga chat dasturini scaling qilish strategiyasini ishlab chiqishga yordam bering.

**Hozirgi holat:**
- Concurrent users: [JORIY SON]
- Expected growth: [O'SISH KUTILAYOTGAN SON]
- Architecture: [HOZIRGI ARXITEKTURA]

**Scaling kerak bo'ladigan joylar:**
1. WebSocket connections
2. Message throughput
3. Database queries
4. Media storage

**Kerakli yechimlar:**
- Horizontal scaling
- Load balancing
- Caching strategies
- Database optimization

Har bir yechimni batafsil tushuntiring.
```

## 🎨 **FRONTEND DESIGN IMPROVEMENT**

### **1. UI/UX Design Prompt**
```
Menga chat dasturining UI/UX ni yaxshilashga yordam bering.

**Joriy dizayn:**
- [JORIY DIZAYN TAFSILOTLARI]
- [MAVJUD MUAMMOLAR/KAMCHILIKLAR]

**Yaxshilanish sohalari:**
1. User experience flow
2. Accessibility (WCAG compliance)
3. Mobile responsiveness
4. Loading states
5. Error messages

**Kerakli natijalar:**
- Mockup takliflari
- Color scheme improvement
- Component redesign
- Animation suggestions

Dizayn takliflaringizni batafsil tushuntiring.
```

## 🔒 **SECURITY ENHANCEMENT**

### **1. Security Audit Prompt**
```
Menga chat dasturimni security audit qilishga yordam bering.

**Dastur tafsilotlari:**
- Texnologiya stack: [RO'YXAT]
- Authentication: [AUTH METODI]
- Data storage: [MA'LUMOTLAR SAQLANISHI]

**Security concernlar:**
1. WebSocket security
2. XSS va injection attacks
3. Authentication bypass
4. Data leakage
5. DoS attacks

**Kerakli yechimlar:**
- Vulnerability scanning
- Penetration testing steps
- Security headers configuration
- Input validation improvements

Har bir zaiflik uchun yechim taklif qiling.
```

## 📈 **BUSINESS FEATURES**

### **1. Monetization Prompt**
```
Menga chat dasturimni monetize qilish strategiyasini ishlab chiqishga yordam bering.

**Dastur xususiyatlari:**
- [ASOSIY FUNKSIYALAR]
- [TARGET AUDIENCE]
- [COMPETITIVE ADVANTAGE]

**Monetization modellari:**
- Freemium model
- Subscription plans
- One-time purchases
- Advertisement
- Enterprise version

**Kerakli:**
- Pricing strategy
- Feature segmentation
- Payment integration
- Analytics tracking

Har bir model uchun implementatsiya bosqichlari bilan tushuntiring.
```

## 💡 **UMUMIY YORDAM PROMPTLARI**

### **1. General Help Prompt**
```
SALOM, MEN [ISMINIZ] ISMIDA DATCHIMAN VA [LOYHA NOMI] USTIDA ISHLAYAPMAN.

**Loyham haqida:**
- Bu WebSocket asosida real vaqtli chat dasturi
- Python Flask backend va JavaScript frontend
- Hozirda [JORIY HOLAT]

**Mening muammom:**
[MUAMMONINGIZNI BATAFSIL TASVIRLANG]

**Menda mavjud:**
- Kod: [KODNING QAYSI QISMI MAVJUD]
- Xatolar: [XATOLIKLAR MAVJUDMI]
- Maqsad: [NIMA QILMOQCHIMAN]

**Men sizdan so'rayman:**
[ANIQ YORDAM SO'RASH]

**Qo'shimcha kontekst:**
- [AGAR QO'SHIMCHA KONTEKST BO'LSA]
```

### **2. Learning Prompt**
```
MEN [TEXNOLOGIYA NOMI] HAQIDA O'RGANMOQCHIMAN VA UNI [LOYHA NOMI] DA QO'LLAMOQCHIMAN.

**Mening darajam:** [BOSHLANG'ICH/ORTA/ILG'OR]
**Vaqtim:** [NECHA SOAT/KUN]

**O'rganish maqsadim:**
- [ANIQ MAQSAD 1]
- [ANIQ MAQSAD 2]
- [ANIQ MAQSAD 3]

**Menga kerak:**
1. Learning path (nimalarni tartib bilan o'rganishim kerak)
2. Amaliy mashqlar (mening loyham bilan bog'liq)
3. Eng yaxshi resurslar (kitoblar, kurslar, dokumentatsiya)
4. Umumiy xatolar va ularni qanday oldini olish kerak

Strukturalangan learning plan berishingizni so'rayman.
```

## 🎭 **PROMPT YOZISH SIRLARI**

### **Eng yaxshi natijalar uchun:**

1. **Aniqlik:** Nima kerakligini aniq yozing
2. **Kontekst:** Loyha haqida ma'lumot bering
3. **Struktura:** Sarlavhalar va bullet pointlar ishlating
4. **Kod:** Xatoliklar va mavjud kodni keltiring
5. **Kutilgan natija:** Nima istayotganingizni aytib qo'ying

### **Misol yaxshi prompt:**
```
MENGA CHAT DASURIMGA "MESSAGE EDITING" FUNKSIYASINI QO'SHISHGA YORDAM BERA OLASANMI?

**Loyha tafsilotlari:**
- Backend: Flask + Socket.IO
- Frontend: Vanilla JavaScript
- Message storage: Memory (keyinroq database qo'shaman)

**Talablar:**
1. Foydalanuvchi o'z xabarini 5 daqiqa ichida o'zgartira olishi
2. Edit qilingan xabarda "edited" belgisi chiqishi
3. Faqat xabar egasi o'zgartira olishi
4. Edit history saqlanishi (agar mumkin bo'lsa)

**Menda mavjud kod struktura:**
- Message object: {id, user, text, time}
- sendMessage() funksiyasi
- socket.on('message') handler

Menga editMessage() funksiyasini yaratishga yordam bering, 
backend va frontend kodlarini ko'rsating.
