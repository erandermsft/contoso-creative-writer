import './app.css';
import { version } from "./version";
import Toolbar from "./components/toolbar";
import Article from "./components/article";
import Task from './components/task';
import ProgressPanel from './components/progress-panel';

function App() {
  return (
    <main className="p-8 flex flex-col min-h-screen bg-gradient-to-b from-blue-50 to-gray-100">
      {/* Header Section */}
      <header className="text-center my-6">
        <h1 className="text-4xl font-bold text-blue-800 bg-gradient-to-r from-blue-600 to-indigo-600 inline-block text-transparent bg-clip-text">Contoso Marketing Team</h1>
        <p className="text-xl text-gray-600 mt-2">
          Your partner in creating engaging content for the Contoso brand.
        </p>
        <hr className="border-2 border-blue-300 my-6 w-3/4 mx-auto rounded-full" />
      </header>
      
      {/* Progress Panel */}
      <div className="container mx-auto px-4 mb-6">
        <ProgressPanel />
      </div>

      {/* Main Content Wrapper */}
      <div className="flex flex-col lg:flex-row lg:space-x-8 mt-8 flex-grow">
        {/* Task Section - Left Aligned */}
        <div className="lg:w-1/3 bg-white p-6 rounded-lg shadow-lg border-t-4 border-blue-500 transition-all hover:shadow-xl lg:self-start lg:sticky lg:top-8">
          <h3 className="text-2xl text-blue-800 font-semibold mb-4">Content Creation Panel</h3>
          <Task />
          <div className="text-center mt-6">
            <Toolbar />
          </div>
        </div>

        {/* Article Section - Right Aligned */}
        <section className="lg:w-2/3 flex-grow mt-8 lg:mt-0 flex flex-col">
          <div className="bg-white shadow-lg rounded-lg p-8 border-t-4 border-indigo-500 transition-all hover:shadow-xl flex flex-col flex-grow overflow-hidden">
            <h2 className="text-3xl text-blue-800 font-semibold mb-4">Your Marketing Content</h2>
            <div className="overflow-y-auto flex-grow" id="content-container">
              <Article />
            </div>
          </div>
          <div>
          </div>
        </section>
      </div>


      {/* Version Number */}
      <div className="fixed right-0 bottom-0 mr-6 mb-2 text-gray-500 bg-white/50 px-2 py-1 rounded-md backdrop-blur-sm">
        v{version}
      </div>
    </main>
  );
}

export default App;

