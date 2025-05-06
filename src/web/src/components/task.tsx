import {
  PaperAirplaneIcon,
  ClipboardDocumentIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/outline";
import { useState } from "react";
import { ISocialMediaPost, IMessage, startWritingTask, generatePlan } from "../store";
import { useAppDispatch } from "../store/hooks";
import { addMessage } from "../store/messageSlice";
import { addArticle, addToCurrentArticle, addSocialMediaPostsToCurrentArticle } from "../store/articleSlice";



// import ImageUpload from "./image-upload";

export const Task = () => {
  const [research, setResearch] = useState("");
  const [products, setProducts] = useState("");
  const [writing, setWriting] = useState("");
  const [influence, setInfluence] = useState("");
  const [goal, setGoal] = useState("");
  const [showDetailedInstructions, setShowDetailedInstructions] = useState(false);

  const dispatch = useAppDispatch();

  const startPlan = async () => {
    // Add a message to indicate the planning has started
    dispatch(addMessage({
      type: "message",
      message: "Planning content creation process..."
    }));
    
    // Generate the plan
    const response = await generatePlan(goal);
    console.log(response);
    
    // Set the form values
    setResearch(response.research);
    setProducts(response.products);
    setWriting(response.assignment);
    setInfluence(response.influencer);
    setShowDetailedInstructions(true);
    
    // Add a message to indicate the planning is complete
    dispatch(addMessage({
      type: "message",
      message: "Content plan created successfully. Ready to begin content creation."
    }));
  };

  const setExample = () => {
    setResearch(
      "Can you find the latest camping trends and what folks are doing in the winter?"
    );
    setProducts("Can you use a selection of tents and sleeping bags as context?");
    setWriting(
      "Write a fun and engaging article that includes the research and product information. The article should be between 800 and 1000 words. Make sure to cite sources in the article as you mention the research not at the end."
    );
    setInfluence("Create a social media campaign that includes the article and product information.");
  };


  const reset = () => {
    setResearch("");
    setProducts("");
    setWriting("");
    setInfluence("");
  };

  const newMessage = (message: IMessage) => {
    dispatch(addMessage(message));
  };

  const newArticle = (article: string) => {
    dispatch(addArticle(article));
  };

  const addToArticle = (text: string) => {
    dispatch(addToCurrentArticle(text));
  };
  const createSocialMediaPosts = (posts: Array<ISocialMediaPost>) => {
    dispatch(addToCurrentArticle("\n\n## Social Media Campaign\n\n"));
    posts.forEach((post: ISocialMediaPost) => {
      dispatch(addSocialMediaPostsToCurrentArticle(post));
    });
  };

  const startWork = () => {
    if (research === "" || products === "" || writing === "") {
      return;
    }
    
    // Add a starting message to initialize the progress panel
    dispatch(addMessage({
      type: "message",
      message: "Starting content creation process..."
    }));
    
    startWritingTask(
      research,
      products,
      writing,
      influence,
      newMessage,
      newArticle,
      addToArticle,
      createSocialMediaPosts
    );
  }

  return (
    <div className="p-3">
      <div className="text-start mt-3">
        <label
          htmlFor="goal"
          className="block text-sm font-medium leading-6 text-gray-900"
        >
          Article creation instructions
        </label>
        <p className="mt-1 text-sm leading-6 text-gray-400">
          What kind of article should the agent team generate?
        </p>
        <div className="mt-2">
          <textarea
            id="goal"
            name="goal"
            rows={3}
            cols={60}
            placeholder="What marketing content would you like to create?"
            className="p-3 block w-full rounded-lg border-0 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-blue-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-500 sm:text-sm sm:leading-6 transition-all duration-200"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
          />
        </div>
        <div className="flex justify-end gap-3 mt-10">
        <button
            type="button"
            className="flex flex-row gap-2 items-center rounded-md bg-white px-4 py-2.5 text-sm font-medium text-gray-800 shadow-sm border border-gray-200 hover:bg-gray-50 transition-all duration-200"
            onClick={() => setShowDetailedInstructions(!showDetailedInstructions)}
          >
             <span>{showDetailedInstructions ? 'Hide Details' : 'Show Details'}</span>
             </button>
          <button
            type="button"
            className="flex flex-row gap-2 items-center rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 transition-all duration-200"
            onClick={startPlan}
          >
            <span>Generate Plan</span>
          </button>
        </div>
      </div>

      {
        showDetailedInstructions ? (
          <div>
            <div className="text-start">
              <label
                htmlFor="research"
                className="block text-sm font-medium leading-6 text-blue-800"
              >
                Research
              </label>
              <p className="mt-1 text-sm leading-6 text-gray-500">
                What kinds of information should our team research?
              </p>
              <div className="mt-2">
                <div className="flex rounded-lg shadow-sm focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500">
                  <textarea
                    id="research"
                    name="research"
                    rows={3}
                    cols={60}
                    placeholder="Enter research topics here..."
                    className="p-3 block w-full rounded-lg border-0 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-blue-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-500 sm:text-sm sm:leading-6 transition-all duration-200"
                    value={research}
                    onChange={(e) => setResearch(e.target.value)}
                  />
                </div>
              </div>
            </div>
            <div className="text-start mt-3">
              <label
                htmlFor="products"
                className="block text-sm font-medium leading-6 text-blue-800"
              >
                Products
              </label>
              <p className="mt-1 text-sm leading-6 text-gray-500">
                Which Contoso products should be featured?
              </p>
              <div className="mt-2">
                <textarea
                  id="products"
                  name="products"
                  rows={3}
                  cols={60}
                  placeholder="Enter product information here..."
                  className="p-3 block w-full rounded-lg border-0 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-blue-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-500 sm:text-sm sm:leading-6 transition-all duration-200"
                  value={products}
                  onChange={(e) => setProducts(e.target.value)}
                />
              </div>
            </div>
            <div className="text-start mt-3">
              <label
                htmlFor="writing"
                className="block text-sm font-medium leading-6 text-blue-800"
              >
                Assignment
              </label>
              <p className="mt-1 text-sm leading-6 text-gray-500">
                What specific type of content should we create?
              </p>
              <div className="mt-2">
                <textarea
                  id="writing"
                  name="writing"
                  rows={3}
                  cols={60}
                  placeholder="Describe the content format and requirements..."
                  className="p-3 block w-full rounded-lg border-0 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-blue-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-500 sm:text-sm sm:leading-6 transition-all duration-200"
                  value={writing}
                  onChange={(e) => setWriting(e.target.value)}
                />
              </div>


            </div>
            <div className="text-start mt-3">
              <label
                htmlFor="influence"
                className="block text-sm font-medium leading-6 text-blue-800"
              >
                Social Media Campaign
              </label>
              <p className="mt-1 text-sm leading-6 text-gray-500">
                What kind of social media posts should be included?
              </p>
              <div className="mt-2">
                <textarea
                  id="influence"
                  name="influence"
                  rows={3}
                  cols={60}
                  placeholder="Describe the social media content needs..."
                  className="p-3 block w-full rounded-lg border-0 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-blue-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-500 sm:text-sm sm:leading-6 transition-all duration-200"
                  value={influence}
                  onChange={(e) => setInfluence(e.target.value)}
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-10">
              <button
                type="button"
                className="flex flex-row gap-2 items-center rounded-md bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm border border-gray-200 hover:bg-gray-50 transition-all duration-200"
                onClick={reset}
              >
                <ArrowPathIcon className="w-5 h-5 text-gray-600" />
                <span>Reset</span>
              </button>

              <button
                type="button"
                className="flex flex-row gap-2 items-center rounded-md bg-gray-100 px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm border border-gray-200 hover:bg-gray-200 transition-all duration-200"
                onClick={setExample}
              >
                <ClipboardDocumentIcon className="w-5 h-5 text-gray-600" />
                <span>Load Example</span>
              </button>
              <button
                type="button"
                className="flex flex-row gap-2 items-center rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 transition-all duration-200"
                onClick={startWork}
              >
                <PaperAirplaneIcon className="w-5 h-5 text-white" />
                <span>Create Content</span>
              </button>
            </div>
          </div>) : (<div></div>)
      }
    </div >
  );
};

export default Task;