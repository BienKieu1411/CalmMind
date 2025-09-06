# 🚀 Hướng dẫn Deploy CalmMind lên Vercel

## 📋 Yêu cầu trước khi deploy

### 1. Tài khoản và API Keys
- **Vercel Account**: Đăng ký tại [vercel.com](https://vercel.com)
- **Groq API Key**: Lấy tại [console.groq.com/keys](https://console.groq.com/keys)
- **Hugging Face Token**: Lấy tại [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### 2. Chuẩn bị Project
- Đảm bảo project đã được commit và push lên GitHub
- Kiểm tra các file cấu hình đã được tạo:
  - `vercel.json` ✅
  - `requirements.txt` ✅
  - `api/analyze.py` ✅

## 🔧 Các bước Deploy

### Bước 1: Cài đặt Vercel CLI (Tùy chọn)
```bash
npm i -g vercel
```

### Bước 2: Deploy qua Vercel Dashboard (Khuyến nghị)

1. **Truy cập Vercel Dashboard**
   - Đăng nhập vào [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"

2. **Import Project**
   - Chọn "Import Git Repository"
   - Chọn repository CalmMind từ GitHub
   - Click "Import"

3. **Cấu hình Project**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (giữ nguyên)
   - **Build Command**: Để trống
   - **Output Directory**: `./client` (cho frontend)

4. **Cấu hình Environment Variables**
   - Trong tab "Environment Variables", thêm:
     ```
     GROQ_API_KEY = your_groq_api_key_here
     HF_TOKEN = your_huggingface_token_here
     ```
   - Click "Add" cho mỗi biến

5. **Deploy**
   - Click "Deploy"
   - Chờ quá trình build hoàn tất (2-3 phút)

### Bước 3: Deploy qua Vercel CLI (Tùy chọn)

```bash
# Di chuyển vào thư mục project
cd /path/to/CalmMind

# Login vào Vercel
vercel login

# Deploy project
vercel

# Cấu hình environment variables
vercel env add GROQ_API_KEY
vercel env add HF_TOKEN

# Redeploy với environment variables
vercel --prod
```

## 🔍 Kiểm tra Deployment

### 1. Kiểm tra URL
- Sau khi deploy thành công, bạn sẽ nhận được URL dạng: `https://your-project-name.vercel.app`
- Truy cập URL để kiểm tra frontend

### 2. Test API Endpoint
```bash
# Test API endpoint
curl -X POST https://your-project-name.vercel.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel very stressed and anxious about work"}'
```

### 3. Kiểm tra Logs
- Vào Vercel Dashboard → Project → Functions
- Xem logs để debug nếu có lỗi

## 🛠️ Troubleshooting

### Lỗi thường gặp:

1. **"Module not found" errors**
   - Kiểm tra `requirements.txt` có đầy đủ dependencies
   - Đảm bảo tất cả imports đều có trong requirements

2. **"Environment variables not found"**
   - Kiểm tra đã cấu hình đúng GROQ_API_KEY và HF_TOKEN
   - Redeploy sau khi thêm environment variables

3. **"Function timeout"**
   - Vercel có giới hạn 10s cho Hobby plan
   - Có thể cần upgrade lên Pro plan cho ML models lớn

4. **"CORS errors"**
   - Kiểm tra CORS configuration trong `api/analyze.py`
   - Đảm bảo allow_origins được set đúng

5. **"Model loading errors"**
   - Kiểm tra Hugging Face token có quyền truy cập model
   - Kiểm tra model ID trong code

### Debug Steps:

1. **Xem Function Logs**
   ```bash
   vercel logs https://your-project-name.vercel.app
   ```

2. **Test Local với Vercel Environment**
   ```bash
   vercel dev
   ```

3. **Kiểm tra Build Logs**
   - Vercel Dashboard → Project → Deployments → Click vào deployment
   - Xem "Build Logs" tab

## 📊 Performance Optimization

### 1. Cold Start Optimization
- Sử dụng `@vercel/python` runtime
- Optimize model loading time
- Consider using smaller models

### 2. Memory Optimization
- Set `maxLambdaSize: "50mb"` trong vercel.json
- Monitor memory usage trong Vercel dashboard

### 3. Caching
- Implement response caching cho model predictions
- Use Vercel Edge Functions nếu cần

## 🔄 Updates và Maintenance

### 1. Update Code
```bash
# Push changes to GitHub
git add .
git commit -m "Update feature"
git push origin main

# Vercel sẽ tự động redeploy
```

### 2. Update Environment Variables
- Vercel Dashboard → Project → Settings → Environment Variables
- Update values và redeploy

### 3. Monitor Performance
- Vercel Dashboard → Project → Analytics
- Monitor function execution time và errors

## 💰 Pricing

### Vercel Hobby Plan (Free)
- 100GB bandwidth/month
- 100 serverless function executions/day
- 10s function timeout
- ✅ Đủ cho development và testing

### Vercel Pro Plan ($20/month)
- Unlimited bandwidth
- 1M serverless function executions/month
- 60s function timeout
- ✅ Khuyến nghị cho production

## 🎯 Production Checklist

- [ ] Environment variables đã được cấu hình
- [ ] API endpoints hoạt động bình thường
- [ ] Frontend load được từ Vercel URL
- [ ] CORS configuration đúng
- [ ] Error handling hoạt động
- [ ] Performance acceptable (< 10s response time)
- [ ] Monitor logs để detect issues

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
2. Xem logs trong Vercel dashboard
3. Test local với `vercel dev`
4. Check GitHub issues của project

---

**Lưu ý**: CalmMind sử dụng ML models và external APIs, có thể có latency cao. Vercel Hobby plan có giới hạn 10s timeout, có thể cần upgrade lên Pro plan cho production use.
