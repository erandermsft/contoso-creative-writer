import Block from "./block";
import { useRemark } from "react-remark";
import remarkGemoji from "remark-gemoji";
import { useAppSelector } from "../store/hooks";
import { useEffect, useRef } from "react";
import "./article.css";

export const Article = () => {
  const [reactContent, setMarkdownSource] = useRemark({
    //@ts-expect-error - this is a bug in the types
    remarkPlugins: [remarkGemoji],
    remarkToRehypeOptions: { allowDangerousHtml: true },
    rehypeReactOptions: {},
  });

  const articles = useAppSelector((state) => state.article);
  const prevArticleLengthRef = useRef<number>(0);

  useEffect(() => {
    setMarkdownSource(articles.currentArticle);
    
    // Check if content is being generated (i.e., content length is increasing)
    if (articles.currentArticle.length > prevArticleLengthRef.current) {
      const contentContainer = document.getElementById('content-container');
      if (contentContainer) {
        // Calculate if we're already at the bottom (or close to it)
        const isNearBottom = contentContainer.scrollHeight - contentContainer.scrollTop - contentContainer.clientHeight < 150;
        
        // Only auto-scroll if we're already near the bottom or if this is a new article
        if (isNearBottom || prevArticleLengthRef.current === 0) {
          // Scroll to the bottom with smooth animation after a short delay to let the content render
          setTimeout(() => {
            contentContainer.scrollTo({
              top: contentContainer.scrollHeight,
              behavior: 'smooth'
            });
          }, 100);
        }
      }
    }
    
    prevArticleLengthRef.current = articles.currentArticle.length;
  }, [articles.currentArticle, setMarkdownSource]);

  return (
    <div className="fade-in">
      <Block 
        innerClassName="text-left prose prose-blue prose-lg max-w-none" 
        outerClassName="mt-6 mb-40 px-2"
      >
        {reactContent}
      </Block>
    </div>
  );
};

export default Article;
