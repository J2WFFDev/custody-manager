import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Kits from './pages/Kits';
import Audit from './pages/Audit';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/kits" element={<Kits />} />
          <Route path="/audit" element={<Audit />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
