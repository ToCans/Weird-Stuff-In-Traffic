'use client';

import React from 'react'; // Removed useState as it's not used here
import TextareaAutosize from 'react-textarea-autosize';
import { IconButton } from './IconButton';
import { ArrowUp } from 'lucide-react';
import { Button } from './Button';

// Define view types (can be imported from a central types file later)
type ActiveView = 'chat' | 'slotmachine' | 'clapwords' | 'fillblank';

// Updated Props Interface
interface PromptInputProps {
	prompt: string;
	setPrompt: (value: string) => void;
	onGenerate: () => void;
	isLoading: boolean;
	disabled: boolean;
	setActiveView: (view: ActiveView) => void; // Keep setActiveView (or rename handleSwitchView here)
	activeView: ActiveView; // Add activeView prop
}

// PromptInput component
export const PromptInput: React.FC<PromptInputProps> = ({
	prompt,
	setPrompt,
	onGenerate,
	isLoading,
	disabled,
	setActiveView, // Destructure the prop (it's handleSwitchView from page.tsx)
	activeView, // Destructure activeView
}) => {
	// Function to send with Enter key
	const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (event.key === 'Enter' && !event.shiftKey && !isLoading && prompt.trim()) {
			event.preventDefault();
			onGenerate();
		}
	};

	// Send when button is clicked
	const handleButtonClick = () => {
		if (!isLoading && prompt.trim()) {
			onGenerate();
		}
	};

	// handleSuggestionClick now directly uses the passed function
	const handleSuggestionClick = (view: ActiveView) => {
		// If the clicked button is already active, switch back to chat view
		if (view === activeView) {
			setActiveView('chat');
		} else {
			// Otherwise, switch to the clicked view
			setActiveView(view);
		}
	};

	// Define base classes for suggestion buttons here for consistency
	const suggestionButtonBaseClasses =
		'text-xs rounded-full font-mono transition-all duration-200 ease-in-out';

	// Determine if the send button should be disabled
	const isSendDisabled = disabled || isLoading || !prompt.trim();

	return (
		// Main container
		<div
			className='box-border flex flex-col items-start p-6 gap-6 w-full bg-[var(--dark-gray)] border-2 border-[var(--gray)] rounded-[32px]'
			id='creative-prompt-input'
		>
			{/* Input area */}
			<div className='relative w-full flex items-center'>
				<TextareaAutosize
					placeholder='Trick the AI...'
					value={prompt}
					onChange={(e) => setPrompt(e.target.value)}
					onKeyDown={handleKeyDown}
					disabled={disabled || isLoading}
					minRows={1}
					maxRows={5}
					className='w-full bg-transparent border-none text-white placeholder-[#666666]-500 focus:outline-none font-mono resize-none overflow-y-auto pr-10 flex-1'
					style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
					aria-label='Prompt input for AI image generation'
				/>
			</div>

			{/* Button row */}
			<div className='w-full flex justify-between items-center'>
				{/* Suggestion buttons */}
				<div id='inspiration-options-container' className='flex flex-wrap gap-2'>
					<Button
						variant={activeView === 'slotmachine' ? 'active' : 'secondary'}
						className={suggestionButtonBaseClasses} // Use base classes here
						size='sm'
						onClick={() => handleSuggestionClick('slotmachine')}
						aria-pressed={activeView === 'slotmachine'}
						aria-label='Open Slot Machine prompt generator'
					>
						Slotmachine
					</Button>
					<Button
						variant={activeView === 'clapwords' ? 'active' : 'secondary'}
						className={suggestionButtonBaseClasses} // Use base classes here
						size='sm'
						onClick={() => handleSuggestionClick('clapwords')}
						aria-pressed={activeView === 'clapwords'}
						aria-label='Open Clap Words prompt generator'
					>
						Clap words
					</Button>
					{/*<Button
            variant={activeView === "fillblank" ? "active" : "secondary"}
            className={suggestionButtonBaseClasses} // Use base classes here
            size="sm"
            onClick={() => handleSuggestionClick("fillblank")}
            aria-pressed={activeView === "fillblank"}
            aria-label="Open Fill in the Blank prompt generator"
          >
            Fill in the blank
          </Button>
          */}
				</div>

				{/* Send button using IconButton */}
				<IconButton
					icon={<ArrowUp size={24} />}
					onClick={handleButtonClick}
					variant='primary'
					ariaLabel='Generate image from prompt' // Pass the aria label
					disabled={isSendDisabled}
				/>
			</div>
		</div>
	);
};
