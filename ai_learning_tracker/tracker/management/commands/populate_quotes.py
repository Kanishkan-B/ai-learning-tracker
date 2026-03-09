from django.core.management.base import BaseCommand
from tracker.models import MotivationalQuote

class Command(BaseCommand):
    help = 'Populate database with motivational quotes'

    def handle(self, *args, **kwargs):
        quotes_data = [
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
            ("Get closer than ever to your customers. So close that you tell them what they need well before they realize it themselves.", "Steve Jobs"),
            ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
            ("It is during our darkest moments that we must focus to see the light.", "Aristotle"),
            ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
            ("The only impossible journey is the one you never begin.", "Tony Robbins"),
            ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
            ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
            ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
            ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs"),
            ("Whether you think you can or you think you can't, you're right.", "Henry Ford"),
            ("The only limit to our realization of tomorrow will be our doubts of today.", "Franklin D. Roosevelt"),
            ("Do not wait to strike till the iron is hot, but make it hot by striking.", "William Butler Yeats"),
            ("Great things are done by a series of small things brought together.", "Vincent Van Gogh"),
            ("What you get by achieving your goals is not as important as what you become by achieving your goals.", "Zig Ziglar"),
            ("You are never too old to set another goal or to dream a new dream.", "C.S. Lewis"),
            ("If you want to lift yourself up, lift up someone else.", "Booker T. Washington"),
            ("I have learned over the years that when one's mind is made up, this diminishes fear.", "Rosa Parks"),
            ("Everything you've ever wanted is on the other side of fear.", "George Addair"),
            ("Believe in yourself. You are braver than you think, more talented than you know.", "Roy T. Bennett"),
            ("I learned that courage was not the absence of fear, but the triumph over it.", "Nelson Mandela"),
            ("There is nothing impossible to they who will try.", "Alexander the Great"),
            ("The secret of getting ahead is getting started.", "Mark Twain"),
            ("It's not whether you get knocked down, it's whether you get up.", "Vince Lombardi"),
            ("Limit your 'always' and your 'nevers.'", "Amy Poehler"),
            ("We generate fears while we sit. We overcome them by action.", "Dr. Henry Link"),
            ("The man who has confidence in himself gains the confidence of others.", "Hasidic Proverb"),
            ("The only person you are destined to become is the person you decide to be.", "Ralph Waldo Emerson"),
            ("Go confidently in the direction of your dreams! Live the life you've imagined.", "Henry David Thoreau"),
            ("Hardships often prepare ordinary people for an extraordinary destiny.", "C.S. Lewis"),
            ("Believe and act as if it were impossible to fail.", "Charles Kettering"),
            ("Life is 10% what happens to me and 90% of how I react to it.", "Charles Swindoll"),
            ("The most difficult thing is the decision to act, the rest is merely tenacity.", "Amelia Earhart"),
            ("How wonderful it is that nobody need wait a single moment before starting to improve the world.", "Anne Frank"),
            ("The question isn't who is going to let me; it's who is going to stop me.", "Ayn Rand"),
            ("Don't be pushed around by the fears in your mind. Be led by the dreams in your heart.", "Roy T. Bennett"),
            ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
            ("When I let go of what I am, I become what I might be.", "Lao Tzu"),
            ("Everything has beauty, but not everyone can see.", "Confucius"),
            ("The journey of a thousand miles begins with one step.", "Lao Tzu"),
            ("Success is walking from failure to failure with no loss of enthusiasm.", "Winston Churchill"),
            ("Just when the caterpillar thought the world was ending, he turned into a butterfly.", "Proverb"),
            ("Change your thoughts and you change your world.", "Norman Vincent Peale"),
            ("Either write something worth reading or do something worth writing.", "Benjamin Franklin"),
            ("The only way to achieve the impossible is to believe it is possible.", "Charles Kingsleigh"),
            ("Happiness is not something readymade. It comes from your own actions.", "Dalai Lama"),
            ("Whatever you can do or dream you can, begin it. Boldness has genius, power and magic in it.", "Johann Wolfgang von Goethe"),
            ("Life isn't about finding yourself. Life is about creating yourself.", "George Bernard Shaw"),
            ("Challenges are what make life interesting and overcoming them is what makes life meaningful.", "Joshua J. Marine"),
        ]
        
        for text, author in quotes_data:
            MotivationalQuote.objects.get_or_create(
                text=text,
                defaults={'author': author}
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {len(quotes_data)} motivational quotes!'))
