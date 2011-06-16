#include <iostream>
#include <string>
#include <vector>

#include "IncludeHandler.h"

#include "llvm/ADT/SmallVector.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/Path.h"
#include "llvm/Support/Regex.h"
#include "llvm/Support/Host.h"

#include "clang/Frontend/Utils.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Basic/FileManager.h"
#include "clang/Lex/PPCallbacks.h"
#include "clang/Lex/PreProcessor.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Lex/HeaderSearch.h"
#include "clang/Basic/FileManager.h"
#include "clang/Parse/ParseAST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/Basic/TargetOptions.h"
#include "clang/Basic/TargetInfo.h"
#include "clang/Rewrite/Rewriter.h"


using namespace llvm;

/*
 * If this flag is specified, the tool will actually rename any headers that
 * match the specified header. The default value is false, which just causes
 * the tool to print where a header was found.
 */ 
static cl::opt<bool>        Rename(
								"rename",
								cl::desc("Renames any headers found"),
								cl::init(false));

static cl::opt<std::string> Filename(
								cl::Positional,
								cl::desc("headerFilename"),
								cl::Required);

static cl::opt<std::string> SearchDir(
								cl::Positional,
								cl::desc("[searchDir]"),
								cl::init(""));

static cl::list<std::string> IncludeDirs(
                                cl::Positional,
                                cl::desc("[includeDir]"));
/*
 * FORWARD DECLARATIONS
 */
std::set<sys::Path> FindFilesContainingHeaders();
bool recurseDirectories(const sys::Path&, std::set<sys::Path>&, std::string*);

/*
 * main 
 */
int main( int argc, char **argv)
{
	cl::ParseCommandLineOptions(argc, argv,
		"Finds inconsistently named headers and shows their location.");
    if( SearchDir.empty())
    {
        SearchDir = sys::Path::GetCurrentDirectory().str();
    }
    FindFilesContainingHeaders();
}

/*
 * FindFilesContainingHeaders
 */
std::set<sys::Path> FindFilesContainingHeaders()
{
    std::set<std::string> candidateFiles;
    sys::Path searchPath(SearchDir);

    std::set<sys::Path> childPaths;
    std::string *errorMsg;

    recurseDirectories(searchPath, childPaths, errorMsg);
    std::set<sys::Path>::iterator childIterator;

    /*
    for( childIterator = childPaths.begin(); childIterator != childPaths.end(); childIterator++)
    {
        std::cout << (*childIterator).str() << std::endl;
    }
    */

    clang::CompilerInstance ci;

    clang::HeaderSearchOptions hsos = ci.getHeaderSearchOpts();
    hsos.AddPath(SearchDir, clang::frontend::Quoted, false, false, false); 
    //hsos.AddPath("/Users/loarabia/Code/uh/test/scenarios/fakeproject", clang::frontend::Quoted,
    //    false, false, false);
    for( int i = 0, e = IncludeDirs.size(); i != e; ++i)
    {
        hsos.AddPath( IncludeDirs[i], clang::frontend::Quoted, false, false,false);
    }

    ci.createFileManager();
    ci.createDiagnostics(0, NULL);

    clang::TargetOptions to;
    to.Triple = llvm::sys::getHostTriple();
    clang::TargetInfo *pti = clang::TargetInfo::CreateTargetInfo(ci.getDiagnostics(), to);
    ci.setTarget(pti);

    clang::ASTConsumer astConsumer;
    clang::LangOptions lOpts;

    for( childIterator = childPaths.begin(); childIterator != childPaths.end(); childIterator++)
    {
        ci.createSourceManager(ci.getFileManager());
        clang::SourceManager &sm = ci.getSourceManager();
        clang::Rewriter rw(sm, lOpts);

        ci.createPreprocessor();
        clang::Preprocessor &pp = ci.getPreprocessor();

        ci.createASTContext();
        
        uh::IncludeHandler *includeHandler = new uh::IncludeHandler(
            ci.getSourceManager(),
            *childIterator,
            Filename,
            rw,
            Rename);

        pp.addPPCallbacks(includeHandler);
        ci.setPreprocessor(&pp);

        clang::ApplyHeaderSearchOptions(
            pp.getHeaderSearchInfo(),
            hsos,
            lOpts,
            pti->getTriple());
        
        ci.InitializeSourceManager( (*childIterator).str());
        ci.getDiagnosticClient().BeginSourceFile(lOpts, &pp);
        clang::ParseAST(pp , &astConsumer, ci.getASTContext());
        ci.getDiagnosticClient().EndSourceFile();
    }
}

/*
 * recurseDirectories - This function scans through
 * the Paths vector and replaces any directories it
 * finds with all the files in that directory (recursively). It uses the
 * sys::Path::getDirectoryContent method to perform the actual directory scans.
 */
bool recurseDirectories(const sys::Path& path,
                   std::set<sys::Path>& result,
                   std::string* ErrMsg)
{
    //llvm::Regex candidateRegEx(".[hHcC][pP]?[pP]?");
    llvm::Regex candidateRegEx("\\.[hc]p?p?",llvm::Regex::IgnoreCase);
    llvm::SmallVector<StringRef,1> matches;

    result.clear();
    std::set<sys::Path> content;
    if (path.getDirectoryContents(content, ErrMsg))
        return true;
    for (std::set<sys::Path>::iterator I = content.begin(), E = content.end();
         I != E;
         ++I) 
         {
             // Make sure it exists and is a directory
             sys::PathWithStatus PwS(*I);
             const sys::FileStatus *Status = PwS.getFileStatus(false, ErrMsg);
             if (!Status)
                return true;
            if (Status->isDir) {
                std::set<sys::Path> moreResults;
                if (recurseDirectories(*I, moreResults, ErrMsg))
                    return true;
                for( std::set<sys::Path>::iterator II = moreResults.begin(),
                    EE = moreResults.end();
                    II != EE;
                    ++II)
                {
                    sys::Path p = *II;
                    StringRef pString(p.str());
                    StringRef ext = sys::path::extension(pString);
                    if(ext.size() > 0 && candidateRegEx.match(ext))
                    {
                        result.insert(*II);
                    }
                    
                }
            } else {
                sys::Path p = *I;
                StringRef pString(p.str());
                StringRef ext = sys::path::extension(pString);
                if(ext.size() > 0 && candidateRegEx.match(ext))
                {
                    result.insert(*I);
                }
            }
        }
    return false;
 }
 
