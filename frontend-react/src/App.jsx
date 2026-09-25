import React, { useState, useRef } from 'react';

// ⚠️ নিচে 127.0.0.1 এর বদলে তোমার Render এর ব্যাকএন্ড লিংকটি বসাও (যেমন: https://factcheck-backend.onrender.com)
const API_BASE_URL = 'https://factcheck-ai-8xx6.onrender.com'; 

function App() {
  const [claim, setClaim] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  
  const fileInputRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setClaim(''); // ছবি দিলে টেক্সট ক্লিয়ার হয়ে যাবে
    }
  };

  const removeImage = () => {
    setImageFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleFactCheck = async (e) => {
    e.preventDefault();
    if (!claim.trim() && !imageFile) {
      setError('যাচাই করার জন্য কোনো টেক্সট লিখুন অথবা একটি ছবি আপলোড করুন।');
      return;
    }

    if (claim.trim().length > 0 && claim.trim().length < 5) {
      setError('টেক্সটটি খুব ছোট। একটু বিস্তারিত লিখুন।');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      let response;
      
      // যদি ছবি আপলোড করা হয়
      if (imageFile) {
        const formData = new FormData();
        formData.append('file', imageFile);

        response = await fetch(`${API_BASE_URL}/api/verify-image`, {
          method: 'POST',
          body: formData, 
        });
      } 
      // যদি শুধু টেক্সট দেওয়া হয়
      else {
        response = await fetch(`${API_BASE_URL}/api/verify-fact`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ claim: claim, language: 'bn' }),
        });
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'সার্ভারের সাথে কানেক্ট করা যাচ্ছে না।');
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'নেটওয়ার্ক বা সার্ভার এরর। ব্যাকএন্ড চালু আছে কি না চেক করুন।');
    } finally {
      setLoading(false);
    }
  };

  const getVerdictColor = (verdict) => {
    if (verdict?.includes('সত্য') || verdict?.includes('True')) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (verdict?.includes('মিথ্যা') || verdict?.includes('Fake')) return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
    if (verdict?.includes('বিভ্রান্তিকর') || verdict?.includes('Misleading')) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-slate-300 border-slate-500/30 bg-slate-500/10';
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans p-4 md:p-8 flex items-center justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-[#0f172a] to-slate-950">
      <div className="w-full max-w-3xl backdrop-blur-xl bg-slate-800/40 border border-slate-700/50 rounded-2xl shadow-2xl p-6 md:p-10">
        
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500 mb-2 drop-shadow-sm">
            FactCheck-AI
          </h1>
          <p className="text-slate-400 text-sm md:text-base">
            খবর, গুজব বা ছবি আপলোড করুন—এআই সাথে সাথে যাচাই করে দেবে।
          </p>
        </div>

        <form onSubmit={handleFactCheck} className="space-y-4">
          
          {/* Text Input */}
          {!imageFile && (
            <div className="relative">
              <textarea
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                placeholder="যাচাই করার জন্য তথ্য বা খবরটি এখানে লিখুন..."
                className="w-full bg-slate-900/50 border border-slate-600 rounded-xl p-5 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all resize-none min-h-[120px]"
              ></textarea>
            </div>
          )}

          {/* Image Upload Preview & Button */}
          <div className="flex flex-col items-center justify-center">
            {imageFile ? (
              <div className="relative w-full bg-slate-900/50 border border-slate-600 rounded-xl p-4 flex flex-col items-center">
                <img src={URL.createObjectURL(imageFile)} alt="Preview" className="max-h-48 rounded-lg object-contain mb-3" />
                <p className="text-sm text-cyan-400 mb-2">{imageFile.name}</p>
                <button type="button" onClick={removeImage} className="text-rose-400 text-sm hover:underline">
                  ছবি মুছে ফেলুন
                </button>
              </div>
            ) : (
              <div className="w-full">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  ref={fileInputRef}
                  className="hidden"
                  id="imageUpload"
                />
                <label 
                  htmlFor="imageUpload" 
                  className="w-full flex items-center justify-center gap-2 py-3 bg-slate-800 border border-dashed border-slate-500 hover:border-cyan-400 rounded-xl cursor-pointer transition-all text-slate-300 hover:text-cyan-400"
                >
                  <span>📷</span> ছবি আপলোড করে যাচাই করুন
                </label>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading || (!claim && !imageFile)}
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold py-4 rounded-xl transition-all shadow-lg hover:shadow-cyan-500/25 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'যাচাই করা হচ্ছে...' : 'সত্যতা যাচাই করুন'}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-center">
            {error}
          </div>
        )}

        {result && !loading && (
          <div className="mt-8 space-y-6 animate-fade-in-up">
            <div className={`p-6 border rounded-xl flex flex-col md:flex-row items-center justify-between gap-4 ${getVerdictColor(result.verdict)}`}>
              <div className="text-center md:text-left">
                <p className="text-sm opacity-80 uppercase tracking-wider font-semibold mb-1">ফলাফল</p>
                <h2 className="text-3xl font-bold">{result.verdict}</h2>
              </div>
              <div className="text-center md:text-right">
                <p className="text-sm opacity-80 uppercase tracking-wider font-semibold mb-1">ট্রাস্ট স্কোর</p>
                <h2 className="text-3xl font-bold">{result.trust_score}%</h2>
              </div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700/50 rounded-xl">
              <h3 className="text-lg font-semibold text-cyan-400 mb-3">বিশ্লেষণ</h3>
              <p className="text-slate-300 leading-relaxed text-sm md:text-base">
                {result.explanation}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;