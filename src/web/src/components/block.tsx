import clsx from "clsx";
import { ReactNode } from "react";

type Props = {
  children: ReactNode;
  outerClassName?: string;
  innerClassName?: string;
};

export const Block = ({ children, outerClassName, innerClassName }: Props) => {
  return (
    <div className={clsx("w-full", outerClassName)}>
      <div
        className={clsx("max-w-screen-xl pl-3 pr-3 xl:mx-auto w-full", innerClassName)}
      >
        {children}
      </div>
    </div>
  );
};

export default Block;
