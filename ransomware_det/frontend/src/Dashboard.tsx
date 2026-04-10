import { useState, useEffect, useRef } from 'react';

interface DetectionLog {
  id: number;
  timestamp: string;
  step: number;
  rfProb: number;
  lstmScore: number;
  decision: string;
  source: string;
}

type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

const Dashboard = () => {
  const [detectionLogs, setDetectionLogs] = useState<DetectionLog[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [stats, setStats] = useState({
    totalDetections: 0,
    normalCount: 0,
    attackCount: 0,
    ransomwareCount: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // WebSocket URL - change this to match your FastAPI server
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/detections';

  // Connect to WebSocket
  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    setConnectionStatus('connecting');

    try {
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.type === 'connected') {
          console.log('Connected to detection stream:', message.message);
        } else if (message.type === 'detection') {
          // Handle incoming detection data
          const newLog: DetectionLog = message.data;

          setDetectionLogs(prev => [newLog, ...prev].slice(0, 50)); // Keep last 50

          setStats(prev => ({
            totalDetections: prev.totalDetections + 1,
            normalCount: prev.normalCount + (newLog.decision === 'BENIGN' || newLog.decision === 'NORMAL' ? 1 : 0),
            attackCount: prev.attackCount + (newLog.decision !== 'BENIGN' && newLog.decision !== 'NORMAL' ? 1 : 0),
            ransomwareCount: prev.ransomwareCount + (newLog.decision.includes('RANSOMWARE') ? 1 : 0),
          }));
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('disconnected');
        setIsRunning(false);

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = window.setTimeout(() => {
          console.log('Attempting to reconnect...');
          connectWebSocket();
        }, 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnectionStatus('error');
    }
  };

  // Disconnect WebSocket
  const disconnectWebSocket = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setConnectionStatus('disconnected');
  };

  // Start detection streaming
  const startDetection = () => {
    if (connectionStatus !== 'connected') {
      connectWebSocket();
      // Wait for connection before sending start command
      const checkConnection = setInterval(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          clearInterval(checkConnection);
          wsRef.current.send(JSON.stringify({ command: 'start' }));
          setIsRunning(true);
        }
      }, 100);
    } else {
      wsRef.current?.send(JSON.stringify({ command: 'start' }));
      setIsRunning(true);
    }
  };

  // Stop detection streaming
  const stopDetection = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command: 'stop' }));
    }
    setIsRunning(false);
  };

  // Reset detection data
  const resetDetection = () => {
    stopDetection();
    setDetectionLogs([]);
    setStats({
      totalDetections: 0,
      normalCount: 0,
      attackCount: 0,
      ransomwareCount: 0,
    });
  };

  // Connect on component mount
  useEffect(() => {
    connectWebSocket();

    return () => {
      disconnectWebSocket();
    };
  }, []);

  const getDecisionColor = (decision: string) => {
    if (decision === 'BENIGN' || decision === 'NORMAL') return 'text-emerald-400';
    if (decision.includes('RANSOMWARE')) return 'text-red-500';
    if (decision.includes('SUSPICIOUS')) return 'text-orange-400';
    return 'text-orange-400';
  };

  const getDecisionBg = (decision: string) => {
    if (decision === 'BENIGN' || decision === 'NORMAL') return 'bg-emerald-500/10 border-emerald-500/30';
    if (decision.includes('RANSOMWARE')) return 'bg-red-500/10 border-red-500/30';
    if (decision.includes('SUSPICIOUS')) return 'bg-orange-500/10 border-orange-500/30';
    return 'bg-orange-500/10 border-orange-500/30';
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-emerald-400';
      case 'connecting': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return '● CONNECTED';
      case 'connecting': return '○ CONNECTING...';
      case 'error': return '● CONNECTION ERROR';
      default: return '○ DISCONNECTED';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#050c19] via-[#0a1628] to-[#050c19]">
      <div className="flex flex-col text-white w-full p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent mb-2">
            R.A.P.P.T.R
          </h1>
          <p className="text-gray-400 text-sm">Ransomware Anomaly Prediction Prevention and Targeted Response</p>
          <p className="text-gray-500 text-xs mt-1">Random Forest + LSTM Detection System</p>

          {/* Connection Status */}
          <div className={`text-xs mt-2 ${getConnectionStatusColor()}`}>
            {getConnectionStatusText()}
          </div>
        </div>

        {/* Control Panel */}
        <div className="flex gap-4 justify-center mb-6">
          <button
            onClick={startDetection}
            disabled={isRunning || connectionStatus === 'connecting'}
            className={`px-6 py-2.5 rounded-lg font-semibold transition-all ${isRunning || connectionStatus === 'connecting'
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 shadow-lg hover:shadow-emerald-500/50'
              }`}
          >
            ▶ Start Detection
          </button>
          <button
            onClick={stopDetection}
            disabled={!isRunning}
            className={`px-6 py-2.5 rounded-lg font-semibold transition-all ${!isRunning
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 shadow-lg hover:shadow-red-500/50'
              }`}
          >
            ⏸ Pause
          </button>
          <button
            onClick={resetDetection}
            className="px-6 py-2.5 rounded-lg font-semibold bg-gray-700 hover:bg-gray-600 transition-all"
          >
            ↻ Reset
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/30 rounded-xl p-5 backdrop-blur-sm">
            <div className="text-blue-400 text-sm font-medium mb-1">Total Detections</div>
            <div className="text-3xl font-bold">{stats.totalDetections}</div>
          </div>
          <div className="bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 border border-emerald-500/30 rounded-xl p-5 backdrop-blur-sm">
            <div className="text-emerald-400 text-sm font-medium mb-1">Normal Traffic</div>
            <div className="text-3xl font-bold">{stats.normalCount}</div>
          </div>
          <div className="bg-gradient-to-br from-orange-500/10 to-orange-600/5 border border-orange-500/30 rounded-xl p-5 backdrop-blur-sm">
            <div className="text-orange-400 text-sm font-medium mb-1">Total Attacks</div>
            <div className="text-3xl font-bold">{stats.attackCount}</div>
          </div>
          <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 border border-red-500/30 rounded-xl p-5 backdrop-blur-sm">
            <div className="text-red-400 text-sm font-medium mb-1">Ransomware</div>
            <div className="text-3xl font-bold">{stats.ransomwareCount}</div>
          </div>
        </div>

        {/* Detection Feed */}
        <div className="bg-gray-900/50 border border-gray-700/50 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="text-cyan-400">●</span> Live Detection Feed
            </h2>
            {isRunning && (
              <span className="text-xs text-emerald-400 animate-pulse">● ACTIVE</span>
            )}
          </div>

          {/* Table Header */}
          <div className="grid grid-cols-7 gap-4 px-4 py-2 bg-gray-800/50 rounded-lg mb-2 text-sm font-semibold text-gray-400">
            <div>Timestamp</div>
            <div>Step</div>
            <div>RF Prob</div>
            <div>LSTM Score</div>
            <div className="col-span-2">Decision</div>
            <div>Source</div>
          </div>

          {/* Detection Logs */}
          <div className="space-y-2 max-h-[500px] overflow-y-auto custom-scrollbar">
            {detectionLogs.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <div className="text-4xl mb-2">🛡️</div>
                <p>No detections yet. Click "Start Detection" to begin monitoring.</p>
                {connectionStatus === 'error' && (
                  <p className="text-red-400 text-sm mt-2">
                    ⚠️ Cannot connect to detection server. Make sure FastAPI is running on {WS_URL}
                  </p>
                )}
              </div>
            ) : (
              detectionLogs.map((log) => (
                <div
                  key={log.id}
                  className={`grid grid-cols-7 gap-4 px-4 py-3 rounded-lg border transition-all hover:scale-[1.01] ${getDecisionBg(
                    log.decision
                  )} animate-fadeIn`}
                >
                  <div className="text-sm text-gray-300">{log.timestamp}</div>
                  <div className="text-sm font-mono">{String(log.step).padStart(4, '0')}</div>
                  <div className="text-sm font-mono text-blue-400">{log.rfProb.toFixed(3)}</div>
                  <div className="text-sm font-mono text-purple-400">{log.lstmScore.toFixed(6)}</div>
                  <div className={`col-span-2 text-sm font-semibold ${getDecisionColor(log.decision)}`}>
                    {log.decision}
                  </div>
                  <div className="text-sm">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${log.source.includes('Random Forest') || log.source === 'RF'
                        ? 'bg-blue-500/20 text-blue-300'
                        : log.source.includes('LSTM')
                          ? 'bg-purple-500/20 text-purple-300'
                          : 'bg-emerald-500/20 text-emerald-300'
                      }`}>
                      {log.source}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(31, 41, 55, 0.5);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(75, 85, 99, 0.8);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(107, 114, 128, 0.9);
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
