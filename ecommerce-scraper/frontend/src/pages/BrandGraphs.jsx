import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";
import "./BrandGraphs.css";

const BrandGraphs = () => {
  const { brand } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/products/filter?brand=${brand}`)
      .then(r => r.json())
      .then(res => setData(res));
  }, [brand]);

  return (
    <div className="graphs-page">
      <h2>{brand} – Products</h2>

      <div className="dashboard-card span-12">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <XAxis dataKey="full_name" hide />
            <YAxis />
            <Tooltip />
            <Bar
              dataKey="sale_price"
              fill="#2563eb"
              onClick={(d) => navigate(`/tv/${d.model_id}`)}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default BrandGraphs;
