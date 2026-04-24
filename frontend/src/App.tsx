import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import BundleResults from './pages/BundleResults';
import Home from './pages/Home';
import RunDemo from './pages/RunDemo';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="demo" element={<RunDemo />} />
        <Route path="results" element={<BundleResults />} />
      </Route>
    </Routes>
  );
}
