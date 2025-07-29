import { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data.message);
      setBackendStatus("✅ Connected");
    } catch (e) {
      console.error(e, `errored out requesting / api`);
      setBackendStatus("❌ Connection failed");
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white">
      <div className="container mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <img 
              src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4" 
              alt="Emergent"
              className="w-16 h-16 rounded-xl shadow-lg"
            />
            <h1 className="text-4xl font-bold ml-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Headout Assignment
            </h1>
          </div>
          <p className="text-xl text-gray-300">Java Application Deployment Automation</p>
          <div className="mt-4 inline-flex items-center px-4 py-2 rounded-full bg-gray-800 border border-gray-700">
            <span className="text-sm">Backend Status: </span>
            <span className="ml-2 text-sm font-semibold">{backendStatus}</span>
          </div>
        </div>

        {/* Assignment Overview */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          <div className="bg-gray-800 rounded-xl p-6 shadow-xl border border-gray-700">
            <h2 className="text-2xl font-semibold mb-4 text-blue-400">📋 Assignment Requirements</h2>
            <ul className="space-y-3 text-gray-300">
              <li className="flex items-center">
                <span className="text-green-400 mr-3">✅</span>
                Clone GitHub repo using SSH
              </li>
              <li className="flex items-center">
                <span className="text-green-400 mr-3">✅</span>
                Start Java application on port 9000
              </li>
              <li className="flex items-center">
                <span className="text-green-400 mr-3">✅</span>
                Create Dockerfile for EC2 deployment
              </li>
              <li className="flex items-center">
                <span className="text-green-400 mr-3">✅</span>
                GitHub Actions CI/CD pipeline
              </li>
              <li className="flex items-center">
                <span className="text-green-400 mr-3">✅</span>
                AWS Elastic Load Balancer setup
              </li>
            </ul>
          </div>

          <div className="bg-gray-800 rounded-xl p-6 shadow-xl border border-gray-700">
            <h2 className="text-2xl font-semibold mb-4 text-purple-400">🚀 Key Features Implemented</h2>
            <ul className="space-y-3 text-gray-300">
              <li className="flex items-center">
                <span className="text-green-400 mr-3">🔧</span>
                Advanced error handling & logging
              </li>
              <li className="flex items-center">
                <span className="text-green-400 mr-3">🏗️</span>
                Infrastructure as Code (Terraform)
              </li>
              <li className="flex items-center">
                <span className="text-green-400 mr-3">🔒</span>
                Security best practices
              </li>
              <li className="flex items-center">
                <span className="text-green-400 mr-3">📊</span>
                Monitoring & health checks
              </li>
              <li className="flex items-center">
                <span className="text-green-400 mr-3">🧪</span>
                Comprehensive testing suite
              </li>
            </ul>
          </div>
        </div>

        {/* Technical Architecture */}
        <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-xl p-8 mb-12 shadow-xl border border-gray-700">
          <h2 className="text-3xl font-semibold mb-6 text-center text-yellow-400">🏗️ Technical Architecture</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🐍</span>
              </div>
              <h3 className="text-lg font-semibold text-blue-400">Deployment Script</h3>
              <p className="text-gray-400 text-sm mt-2">Python script with SSH cloning, process management, and error handling</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🐳</span>
              </div>
              <h3 className="text-lg font-semibold text-purple-400">Containerization</h3>
              <p className="text-gray-400 text-sm mt-2">Multi-stage Dockerfile with Amazon Corretto and security best practices</p>
            </div>
            <div className="text-center">
              <div className="bg-green-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">☁️</span>
              </div>
              <h3 className="text-lg font-semibold text-green-400">AWS Infrastructure</h3>
              <p className="text-gray-400 text-sm mt-2">ALB, ECS Fargate, Auto Scaling, VPC, and monitoring setup</p>
            </div>
          </div>
        </div>

        {/* Files Created */}
        <div className="bg-gray-800 rounded-xl p-6 shadow-xl border border-gray-700 mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-cyan-400">📁 Solution Files</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center p-3 bg-gray-700 rounded-lg">
                <span className="text-yellow-400 mr-3">📜</span>
                <span className="font-mono text-sm">deploy.py</span>
                <span className="ml-auto text-xs text-gray-400">Main deployment script</span>
              </div>
              <div className="flex items-center p-3 bg-gray-700 rounded-lg">
                <span className="text-blue-400 mr-3">🐳</span>
                <span className="font-mono text-sm">Dockerfile</span>
                <span className="ml-auto text-xs text-gray-400">Container configuration</span>
              </div>
              <div className="flex items-center p-3 bg-gray-700 rounded-lg">
                <span className="text-green-400 mr-3">⚙️</span>
                <span className="font-mono text-sm">deploy.yml</span>
                <span className="ml-auto text-xs text-gray-400">GitHub Actions CI/CD</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center p-3 bg-gray-700 rounded-lg">
                <span className="text-orange-400 mr-3">🏗️</span>
                <span className="font-mono text-sm">main.tf</span>
                <span className="ml-auto text-xs text-gray-400">Terraform infrastructure</span>
              </div>
              <div className="flex items-center p-3 bg-gray-700 rounded-lg">
                <span className="text-purple-400 mr-3">🧪</span>
                <span className="font-mono text-sm">test_deploy.py</span>
                <span className="ml-auto text-xs text-gray-400">Unit tests</span>
              </div>
              <div className="flex items-center p-3 bg-gray-700 rounded-lg">
                <span className="text-pink-400 mr-3">📚</span>
                <span className="font-mono text-sm">README.md</span>
                <span className="ml-auto text-xs text-gray-400">Documentation</span>
              </div>
            </div>
          </div>
        </div>

        {/* Load Balancer Configuration */}
        <div className="bg-gradient-to-r from-blue-900 to-purple-900 rounded-xl p-6 shadow-xl border border-blue-700 mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-blue-300">⚖️ Load Balancer Configuration</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Parameters Set:</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Health checks every 30 seconds on /health</li>
                <li>• 2 healthy checks before routing traffic</li>
                <li>• 3 unhealthy checks trigger removal</li>
                <li>• Auto scaling: CPU 70%, Memory 80%</li>
                <li>• Cross-zone load balancing enabled</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Why These Settings:</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• 30s interval: AWS standard recommendation</li>
                <li>• 2/3 thresholds: Quick recovery, avoid flapping</li>
                <li>• CPU 70%: Headroom for traffic spikes</li>
                <li>• Memory 80%: More predictable than CPU</li>
                <li>• Cross-zone: Even traffic distribution</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl p-8 shadow-xl">
            <h2 className="text-3xl font-bold mb-4">🎉 Assignment Complete!</h2>
            <p className="text-xl mb-6 text-gray-100">
              Production-ready DevOps automation solution with comprehensive error handling, 
              security best practices, and scalable architecture.
            </p>
            <div className="flex justify-center space-x-4">
              <button className="bg-white text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                📚 View Documentation
              </button>
              <button className="bg-gray-800 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors border border-gray-600">
                🚀 Run Demo Script
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-400 text-sm">
          <p>Built with React + FastAPI + MongoDB | Deployed with love 💙</p>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
