import { githubDevSubsPort } from "../utils/ghutils";
export interface IMessage {
  type: "message" | "researcher" | "marketing" | "writer" | "editor" | "error" | "partial" | "influencer";
  message: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: any;
}

export interface ISocialMediaPost{
  customer: string,
  socialMediaPost: string
}

export interface IArticleCollection {
  current: number;
  articles: string[];
  currentArticle: string;
}

export interface IChatTurn {
  name: string;
  avatar: string;
  image: string | null;
  message: string;
  status: "waiting" | "done";
  type: "user" | "assistant";
}

export const generatePlan = async (goal:string) => {

  const configuration = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Connection": "keep-alive",
    },
    body: JSON.stringify({
      goal: goal

    }),
    
  };
  const hostname = window.location.hostname;
  const apiPort = 8000;
  
  const endpoint =
    (hostname === 'localhost' || hostname === '127.0.0.1')
      ? `http://localhost:${apiPort}`
      : hostname.endsWith('github.dev')
      ? `${githubDevSubsPort(hostname, apiPort)}/`
      : "";
  const url = `${
    endpoint.endsWith("/") ? endpoint : endpoint + "/"
  }api/plan`;

  const callPlannerApi = async () => {
    try {
      const response = await fetch(url, configuration);
      return response.json();
    
    } catch (e) {
      console.log(e);
    }
  };

  return callPlannerApi();
}

export const startWritingTask = (
  research: string,
  products: string,
  assignment: string,
  influence:string,
  addMessage: { (message: IMessage): void },
  createArticle: { (article: string): void },
  addToArticle: { (text: string): void },
  createSocialMediaPosts:{(posts:Array<ISocialMediaPost>):void}
) => {
  // internal function to read chunks from a stream
  function readChunks(reader: ReadableStreamDefaultReader<Uint8Array>) {
    return {
      async *[Symbol.asyncIterator]() {
        let readResult = await reader.read();
        while (!readResult.done) {
          yield readResult.value;
          readResult = await reader.read();
        }
      },
    };
  }

  const configuration = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Connection": "keep-alive",
    },
    body: JSON.stringify({
      research: research,
      products: products,
      assignment: assignment,
      influence: influence

    }),
  };

  const hostname = window.location.hostname;
  const apiPort = 8000;
  
  const endpoint =
    (hostname === 'localhost' || hostname === '127.0.0.1')
      ? `http://localhost:${apiPort}`
      : hostname.endsWith('github.dev')
      ? `${githubDevSubsPort(hostname, apiPort)}/`
      : "";


  const url = `${
    endpoint.endsWith("/") ? endpoint : endpoint + "/"
  }api/article`;

  const callApi = async () => {
    try {
      const response = await fetch(url, configuration);
      const reader = response.body?.getReader();
      if (!reader) return;

      const chunks = readChunks(reader);
      for await (const chunk of chunks) {
        const text = new TextDecoder().decode(chunk);
        const parts = text.split("\n");
        for (let part of parts) {
          part = part.trim();
          if (!part || part.length === 0) continue;
          // console.log(part);
          const message = JSON.parse(part) as IMessage;
          addMessage(message);
          if (message.type === "writer") {
            if (message.data && message.data.start) {
              createArticle("");
            }
          }else if(message.type === "influencer") {
            console.log('creating social media posts');
            createSocialMediaPosts(JSON.parse(message.data?.posts) || []);
          }
           else if (message.type === "partial") {
            if (message.data?.text && message.data.text.length > 0) {
              addToArticle(message.data?.text || "");
              // console.log('adding to article');
            }
            else {
              console.log('writing complete');
            }

          }
          
        }
      }
    } catch (e) {
      console.log(e);
    }
  };

  callApi();

};