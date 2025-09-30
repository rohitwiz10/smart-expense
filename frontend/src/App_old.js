import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Tabs,
  Tab,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Card,
  CardContent,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  TrendingUp as TrendingUpIcon,
  Category as CategoryIcon,
  AccountBalance as BudgetIcon,
  Receipt as ExpenseIcon,
  Psychology as InsightsIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  return (
    <Router>
      <MainApp />
    </Router>
  );
}

function MainApp() {
  const location = useLocation();
  const [currentTab, setCurrentTab] = useState(0);

  useEffect(() => {
    const pathToTab = {
      '/': 0,
      '/expenses': 0,
      '/categories': 1,
      '/budgets': 2,
      '/analytics': 3,
      '/insights': 4,
    };
    setCurrentTab(pathToTab[location.pathname] || 0);
  }, [location]);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <Toolbar>
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            💰 Expense Manager
          </Typography>
        </Toolbar>
        <Tabs
          value={currentTab}
          onChange={(e, newValue) => setCurrentTab(newValue)}
          textColor="inherit"
          sx={{ borderTop: '1px solid rgba(255,255,255,0.2)' }}
        >
          <Tab label="Expenses" icon={<ExpenseIcon />} component={Link} to="/expenses" />
          <Tab label="Categories" icon={<CategoryIcon />} component={Link} to="/categories" />
          <Tab label="Budgets" icon={<BudgetIcon />} component={Link} to="/budgets" />
          <Tab label="Analytics" icon={<TrendingUpIcon />} component={Link} to="/analytics" />
          <Tab label="AI Insights" icon={<InsightsIcon />} component={Link} to="/insights" />
        </Tabs>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<ExpensesPage />} />
          <Route path="/expenses" element={<ExpensesPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/budgets" element={<BudgetsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/insights" element={<InsightsPage />} />
        </Routes>
      </Container>
    </Box>
  );
}

// ==================== EXPENSES PAGE ====================
function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingExpense, setEditingExpense] = useState(null);
  const [formData, setFormData] = useState({
    amount: '',
    category_id: '',
    description: '',
    date: format(new Date(), 'yyyy-MM-dd'),
  });

  useEffect(() => {
    fetchExpenses();
    fetchCategories();
  }, []);

  const fetchExpenses = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/expenses`);
      setExpenses(response.data);
    } catch (error) {
      console.error('Error fetching expenses:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleOpenDialog = (expense = null) => {
    if (expense) {
      setEditingExpense(expense);
      setFormData({
        amount: expense.amount,
        category_id: expense.category_id,
        description: expense.description,
        date: expense.date,
      });
    } else {
      setEditingExpense(null);
      setFormData({
        amount: '',
        category_id: '',
        description: '',
        date: format(new Date(), 'yyyy-MM-dd'),
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingExpense(null);
  };

  const handleSubmit = async () => {
    try {
      if (editingExpense) {
        await axios.put(`${API_URL}/api/expenses/${editingExpense.id}`, {
          ...formData,
          id: editingExpense.id,
          amount: parseFloat(formData.amount),
        });
      } else {
        await axios.post(`${API_URL}/api/expenses`, {
          ...formData,
          amount: parseFloat(formData.amount),
        });
      }
      fetchExpenses();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving expense:', error);
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await axios.delete(`${API_URL}/api/expenses/${id}`);
        fetchExpenses();
      } catch (error) {
        console.error('Error deleting expense:', error);
      }
    }
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find((c) => c.id === categoryId);
    return category ? category.name : 'Unknown';
  };

  const getCategoryColor = (categoryId) => {
    const category = categories.find((c) => c.id === categoryId);
    return category ? category.color : '#3b82f6';
  };

  const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Expenses
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>
          Add Expense
        </Button>
      </Box>

      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <CardContent>
          <Typography variant="h6">Total Expenses</Typography>
          <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
            ${totalExpenses.toFixed(2)}
          </Typography>
          <Typography variant="body2">{expenses.length} transactions</Typography>
        </CardContent>
      </Card>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Description</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Category</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="right">
                Amount
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="center">
                Actions
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {expenses.map((expense) => (
              <TableRow key={expense.id} hover>
                <TableCell>{format(new Date(expense.date), 'MMM dd, yyyy')}</TableCell>
                <TableCell>{expense.description}</TableCell>
                <TableCell>
                  <Chip
                    label={getCategoryName(expense.category_id)}
                    size="small"
                    sx={{
                      backgroundColor: getCategoryColor(expense.category_id),
                      color: 'white',
                      fontWeight: 'bold',
                    }}
                  />
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', color: '#d32f2f' }}>
                  ${expense.amount.toFixed(2)}
                </TableCell>
                <TableCell align="center">
                  <IconButton size="small" color="primary" onClick={() => handleOpenDialog(expense)}>
                    <EditIcon />
                  </IconButton>
                  <IconButton size="small" color="error" onClick={() => handleDelete(expense.id)}>
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingExpense ? 'Edit Expense' : 'Add Expense'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Amount"
            type="number"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            sx={{ mt: 2 }}
          />
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={formData.category_id}
              onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
              label="Category"
            >
              {categories.map((cat) => (
                <MenuItem key={cat.id} value={cat.id}>
                  {cat.icon} {cat.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            sx={{ mt: 2 }}
          />
          <TextField
            fullWidth
            label="Date"
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
            sx={{ mt: 2 }}
            InputLabelProps={{ shrink: true }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            {editingExpense ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

// ==================== CATEGORIES PAGE ====================
function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({ name: '', color: '#3b82f6', icon: '💰' });

  const iconOptions = ['💰', '🍔', '🚗', '🏠', '💊', '🎬', '🛒', '✈️', '📱', '👕', '🎓', '⚡'];

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleOpenDialog = (category = null) => {
    if (category) {
      setEditingCategory(category);
      setFormData({ name: category.name, color: category.color, icon: category.icon });
    } else {
      setEditingCategory(null);
      setFormData({ name: '', color: '#3b82f6', icon: '💰' });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingCategory(null);
  };

  const handleSubmit = async () => {
    try {
      if (editingCategory) {
        await axios.put(`${API_URL}/api/categories/${editingCategory.id}`, {
          ...formData,
          id: editingCategory.id,
        });
      } else {
        await axios.post(`${API_URL}/api/categories`, formData);
      }
      fetchCategories();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving category:', error);
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this category?')) {
      try {
        await axios.delete(`${API_URL}/api/categories/${id}`);
        fetchCategories();
      } catch (error) {
        alert('Error: ' + (error.response?.data?.detail || error.message));
      }
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Categories
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>
          Add Category
        </Button>
      </Box>

      <Grid container spacing={3}>
        {categories.map((category) => (
          <Grid item xs={12} sm={6} md={4} key={category.id}>
            <Card sx={{ borderLeft: `4px solid ${category.color}` }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h3">{category.icon}</Typography>
                    <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                      {category.name}
                    </Typography>
                  </Box>
                  <Box>
                    <IconButton size="small" color="primary" onClick={() => handleOpenDialog(category)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(category.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingCategory ? 'Edit Category' : 'Add Category'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Category Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            sx={{ mt: 2 }}
          />
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Icon</InputLabel>
            <Select
              value={formData.icon}
              onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
              label="Icon"
            >
              {iconOptions.map((icon) => (
                <MenuItem key={icon} value={icon}>
                  <Typography variant="h6">{icon}</Typography>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Color"
            type="color"
            value={formData.color}
            onChange={(e) => setFormData({ ...formData, color: e.target.value })}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            {editingCategory ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

// ==================== BUDGETS PAGE ====================
function BudgetsPage() {
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingBudget, setEditingBudget] = useState(null);
  const [formData, setFormData] = useState({
    category_id: '',
    amount: '',
    month: format(new Date(), 'yyyy-MM'),
  });

  useEffect(() => {
    fetchBudgets();
    fetchCategories();
    fetchExpenses();
  }, []);

  const fetchBudgets = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/budgets`);
      setBudgets(response.data);
    } catch (error) {
      console.error('Error fetching budgets:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchExpenses = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/expenses`);
      setExpenses(response.data);
    } catch (error) {
      console.error('Error fetching expenses:', error);
    }
  };

  const handleOpenDialog = (budget = null) => {
    if (budget) {
      setEditingBudget(budget);
      setFormData({
        category_id: budget.category_id,
        amount: budget.amount,
        month: budget.month,
      });
    } else {
      setEditingBudget(null);
      setFormData({
        category_id: '',
        amount: '',
        month: format(new Date(), 'yyyy-MM'),
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingBudget(null);
  };

  const handleSubmit = async () => {
    try {
      if (editingBudget) {
        await axios.put(`${API_URL}/api/budgets/${editingBudget.id}`, {
          ...formData,
          id: editingBudget.id,
          amount: parseFloat(formData.amount),
        });
      } else {
        await axios.post(`${API_URL}/api/budgets`, {
          ...formData,
          amount: parseFloat(formData.amount),
        });
      }
      fetchBudgets();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving budget:', error);
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this budget?')) {
      try {
        await axios.delete(`${API_URL}/api/budgets/${id}`);
        fetchBudgets();
      } catch (error) {
        console.error('Error deleting budget:', error);
      }
    }
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find((c) => c.id === categoryId);
    return category ? category.name : 'Unknown';
  };

  const getActualSpending = (categoryId, month) => {
    return expenses
      .filter((exp) => exp.category_id === categoryId && exp.date.startsWith(month))
      .reduce((sum, exp) => sum + exp.amount, 0);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Monthly Budgets
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>
          Add Budget
        </Button>
      </Box>

      <Grid container spacing={3}>
        {budgets.map((budget) => {
          const actual = getActualSpending(budget.category_id, budget.month);
          const percentage = (actual / budget.amount) * 100;
          const isOverBudget = actual > budget.amount;

          return (
            <Grid item xs={12} sm={6} md={4} key={budget.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                      {getCategoryName(budget.category_id)}
                    </Typography>
                    <Box>
                      <IconButton size="small" color="primary" onClick={() => handleOpenDialog(budget)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDelete(budget.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {format(new Date(budget.month + '-01'), 'MMMM yyyy')}
                  </Typography>
                  <Box sx={{ position: 'relative', display: 'inline-flex', width: '100%', justifyContent: 'center', mb: 2 }}>
                    <CircularProgress
                      variant="determinate"
                      value={Math.min(percentage, 100)}
                      size={100}
                      thickness={5}
                      sx={{
                        color: isOverBudget ? '#d32f2f' : percentage > 80 ? '#ff9800' : '#4caf50',
                      }}
                    />
                    <Box
                      sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
                        {percentage.toFixed(0)}%
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Spent
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 'bold', color: isOverBudget ? '#d32f2f' : 'inherit' }}>
                        ${actual.toFixed(2)}
                      </Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography variant="caption" color="text.secondary">
                        Budget
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                        ${budget.amount.toFixed(2)}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingBudget ? 'Edit Budget' : 'Add Budget'}</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={formData.category_id}
              onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
              label="Category"
            >
              {categories.map((cat) => (
                <MenuItem key={cat.id} value={cat.id}>
                  {cat.icon} {cat.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Budget Amount"
            type="number"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            sx={{ mt: 2 }}
          />
          <TextField
            fullWidth
            label="Month"
            type="month"
            value={formData.month}
            onChange={(e) => setFormData({ ...formData, month: e.target.value })}
            sx={{ mt: 2 }}
            InputLabelProps={{ shrink: true }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            {editingBudget ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

// ==================== ANALYTICS PAGE ====================
function AnalyticsPage() {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/analytics/summary`);
      setAnalyticsData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!analyticsData) {
    return <Typography>No data available</Typography>;
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
        Analytics Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6">Total Expenses</Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                ${analyticsData.total_expenses.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6">Total Budget</Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                ${analyticsData.total_budget.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Spending by Category - Pie Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Spending by Category
              </Typography>
              {analyticsData.category_spending.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData.category_spending}
                      dataKey="amount"
                      nameKey="category"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label={(entry) => `${entry.category}: $${entry.amount.toFixed(2)}`}
                    >
                      {analyticsData.category_spending.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography>No data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Monthly Trends - Line Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Monthly Spending Trends
              </Typography>
              {analyticsData.monthly_trends.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.monthly_trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="amount" stroke="#667eea" strokeWidth={2} name="Amount ($)" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Typography>No data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Budget vs Actuals - Bar Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Budget vs Actual Spending
              </Typography>
              {analyticsData.budget_comparison.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.budget_comparison}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="budget" fill="#4caf50" name="Budget ($)" />
                    <Bar dataKey="actual" fill="#d32f2f" name="Actual ($)" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography>No budgets set. Add budgets to see comparison.</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

// ==================== INSIGHTS PAGE ====================
function InsightsPage() {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/insights`);
      setInsights(response.data);
    } catch (error) {
      console.error('Error fetching insights:', error);
      alert('Error generating insights: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          AI-Powered Insights
        </Typography>
        <Button variant="contained" onClick={fetchInsights} disabled={loading}>
          {loading ? 'Generating...' : 'Refresh Insights'}
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
          <CircularProgress />
        </Box>
      ) : insights ? (
        <>
          {insights.summary && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="caption" color="text.secondary">
                      Total Expenses
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                      ${insights.summary.total_expenses?.toFixed(2) || '0.00'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="caption" color="text.secondary">
                      Transactions
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                      {insights.summary.num_transactions || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="caption" color="text.secondary">
                      Categories
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                      {insights.summary.categories || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="caption" color="text.secondary">
                      Budgets Set
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                      {insights.summary.budgets_set || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <InsightsIcon sx={{ fontSize: 40, color: '#667eea' }} />
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  AI Analysis
                </Typography>
              </Box>
              <Typography
                variant="body1"
                sx={{
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.8,
                  fontSize: '1.1rem',
                }}
              >
                {insights.insights}
              </Typography>
            </CardContent>
          </Card>
        </>
      ) : (
        <Typography>No insights available</Typography>
      )}
    </Box>
  );
}

export default App;
