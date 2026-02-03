import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";
import "./PlatformGraphs.css";

const PlatformGraphs = () => {
  const { platform } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/products/filter?platform=${platform}`)
      .then(r => r.json())
      .then(res => setData(res));
  }, [platform]);

  return (
    <div className="graphs-page">
      <h2>{platform} – Products</h2>

      <div className="dashboard-card span-12">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <XAxis dataKey="brand" />
            <YAxis />
            <Tooltip />
            <Bar
              dataKey="sale_price"
              fill="#16a34a"
              onClick={(d) => navigate(`/tv/${d.model_id}`)}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default PlatformGraphs;
