/**
 * Admin User Management Page
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { adminAPI } from "../services/api";
import "./AdminUsers.css";

const AdminUsers = () => {
  const navigate = useNavigate();
  const { user, isAdmin } = useAuth();
  
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({ role: "", verified: "" });

  useEffect(() => {
    if (!user || !isAdmin()) {
      navigate("/unauthorized");
      return;
    }
    fetchUsers();
  }, [page, search, filters]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        page_size: 20,
        ...(search && { search }),
        ...(filters.role && { role: filters.role }),
        ...(filters.verified !== "" && { verified: filters.verified === "true" })
      };
      
      const response = await adminAPI.getUsers(params);
      setUsers(response.data.users);
      setTotalPages(response.data.total_pages);
    } catch (err) {
      console.error("Failed to fetch users:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (userId, currentStatus) => {
    try {
      await adminAPI.updateUser(userId, { is_active: !currentStatus });
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update user");
    }
  };

  const handleToggleVerified = async (userId, currentStatus) => {
    try {
      await adminAPI.updateUser(userId, { is_verified: !currentStatus });
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update user");
    }
  };

  const handleChangeRole = async (userId, newRole) => {
    try {
      await adminAPI.updateUser(userId, { role: newRole });
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update role");
    }
  };

  const handleDelete = async (userId, userName) => {
    if (!window.confirm(`Delete user "${userName}"? This cannot be undone.`)) return;
    
    try {
      await adminAPI.deleteUser(userId);
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete user");
    }
  };

  return (
    <div className="admin-users">
      <div className="container py-4">
        {/* Header */}
        <div className="page-header">
          <div>
            <button className="btn btn-link" onClick={() => navigate("/admin")}>
              ← Back to Dashboard
            </button>
            <h1>User Management</h1>
          </div>
        </div>

        {/* Filters */}
        <div className="filters-bar">
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          
          <select
            value={filters.role}
            onChange={(e) => setFilters({ ...filters, role: e.target.value })}
          >
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="user">User</option>
          </select>
          
          <select
            value={filters.verified}
            onChange={(e) => setFilters({ ...filters, verified: e.target.value })}
          >
            <option value="">All Status</option>
            <option value="true">Verified</option>
            <option value="false">Unverified</option>
          </select>
        </div>

        {/* Users Table */}
        <div className="users-table-container">
          {loading ? (
            <div className="loading-container">
              <div className="spinner-border text-warning"></div>
            </div>
          ) : (
            <table className="users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Verified</th>
                  <th>Active</th>
                  <th>Wishlists</th>
                  <th>Alerts</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className={!u.is_active ? "inactive" : ""}>
                    <td>{u.id}</td>
                    <td>{u.name}</td>
                    <td>{u.email}</td>
                    <td>
                      <select
                        value={u.role}
                        onChange={(e) => handleChangeRole(u.id, e.target.value)}
                        className={`role-select ${u.role}`}
                        disabled={u.id === user?.id}
                      >
                        <option value="user">User</option>
                        <option value="admin">Admin</option>
                      </select>
                    </td>
                    <td>
                      <button
                        className={`status-btn ${u.is_verified ? "verified" : "unverified"}`}
                        onClick={() => handleToggleVerified(u.id, u.is_verified)}
                      >
                        {u.is_verified ? "✓ Verified" : "○ Pending"}
                      </button>
                    </td>
                    <td>
                      <button
                        className={`status-btn ${u.is_active ? "active" : "inactive"}`}
                        onClick={() => handleToggleActive(u.id, u.is_active)}
                        disabled={u.id === user?.id}
                      >
                        {u.is_active ? "✓ Active" : "✕ Inactive"}
                      </button>
                    </td>
                    <td>{u.wishlist_count}</td>
                    <td>{u.alert_count}</td>
                    <td>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="btn-delete"
                        onClick={() => handleDelete(u.id, u.name)}
                        disabled={u.id === user?.id}
                        title="Delete User"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        <div className="pagination">
          <button
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
          >
            ← Previous
          </button>
          <span>Page {page} of {totalPages}</span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(p => p + 1)}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminUsers;