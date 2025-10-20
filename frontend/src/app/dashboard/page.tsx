"use client"
import { useEffect, useState } from "react";

interface EC2Instance {
  id: string;
  state: string;
}

interface DashboardData {
  unused_instances: EC2Instance[];
}

export default function Dashboard() {
  const [ec2, setEc2] = useState<EC2Instance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8084/api";

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${apiUrl}/ec2/unused`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data: DashboardData = await response.json();
        setEc2(data.unused_instances || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch data");
        console.error("Error fetching EC2 instances:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [apiUrl]);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-semibold mb-4">AWS Cleanup Dashboard</h1>
      
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-xl mb-2">Stopped EC2 Instances</h2>
        
        {loading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <span className="ml-3 text-gray-600">Loading instances...</span>
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}
        
        {!loading && !error && ec2.length === 0 && (
          <p className="text-gray-500 py-4">No stopped EC2 instances found.</p>
        )}
        
        {!loading && !error && ec2.length > 0 && (
          <ul>
            {ec2.map((instance) => (
              <li key={instance.id} className="border-b py-2 flex justify-between items-center">
                <span className="font-mono text-sm">{instance.id}</span>
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                  {instance.state}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
